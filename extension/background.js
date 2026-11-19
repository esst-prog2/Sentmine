// The right-click items. On selected text: make its card, with the text just around the selection, so sentmine can
// take the whole sentences it touches as the passage. On an image: put it on the card last
// made or edited. The right-click lets the extension see that one tab (activeTab), and nothing else.
import { MENU, NO_CARD_YET, PICTURE_MENU, boxOnShot, clipFor, findSentmine, storedSize, withContext } from "./logic.js";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    for (const [id, title] of Object.entries(MENU)) {
      chrome.contextMenus.create({ id, title, contexts: ["selection"] });
    }
    chrome.contextMenus.create({ id: "picture", title: PICTURE_MENU.picture, contexts: ["image"] });
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  // The panel must be opened at once, while the click still counts as the reader's own action.
  if (tab && tab.windowId !== undefined) chrome.sidePanel.open({ windowId: tab.windowId }).catch(() => {});
  const work = info.menuItemId in PICTURE_MENU ? addPicture(info, tab) : sendClip(info, tab);
  work.then((news) => chrome.runtime.sendMessage(news).catch(() => {}));   // the panel may still be opening
});

export async function sendClip(info, tab) {
  let clip = clipFor(info.menuItemId, info.selectionText);
  if (clip.refuse) return { clip: "refused", message: clip.refuse };
  const base = await findSentmine(fetch);
  if (!base) return { clip: "no-sentmine" };
  try {   // the browser's own PDF viewer and its own pages cannot be read: the selection alone is sent
    const [result] = await chrome.scripting.executeScript({ target: { tabId: tab.id, frameIds: [info.frameId || 0] }, func: aroundSelection });
    clip = withContext(clip, result && result.result);
  } catch (error) {
    // keep the selection as the browser gave it
  }
  try {
    const response = await fetch(base + "/clip/api/text", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...clip, source: { title: (tab && tab.title) || "", url: info.pageUrl || (tab && tab.url) || "" } }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) return { clip: "refused", message: data.error || "sentmine could not read it." };
  } catch (error) {
    return { clip: "no-sentmine" };
  }
  return { clip: "added", base };
}

// --- pictures ---------------------------------------------------------------------------------

export async function addPicture(info, tab) {
  const base = await findSentmine(fetch);
  if (!base) return { clip: "no-sentmine" };
  let card;
  try {
    const state = await (await fetch(base + "/clip/api/state")).json();
    card = state.cards.find((one) => one.id === state.chosen_card) || state.cards[state.cards.length - 1];
  } catch (error) {
    return { clip: "no-sentmine" };
  }
  if (!card) return { clip: "refused", message: NO_CARD_YET };
  let png;
  try {
    png = await imagePng(info.srcUrl, tab);
  } catch (error) {
    return { clip: "refused", message: error.message };
  }
  if (!png) return { clip: "refused", message: "No picture added." };
  const response = await fetch(base + "/clip/api/cards/" + card.id + "/pictures", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ png: base64(png) }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) return { clip: "refused", message: data.error || "sentmine could not take the picture." };
  return { clip: "added", base };
}

// An image as it is when the site allows it to be downloaded again; otherwise what the window shows of it.
async function imagePng(source, tab) {
  try {
    const response = await fetch(source);
    if (response.ok) return await asPng(await createImageBitmap(await response.blob()));
  } catch (error) {
    // the site does not allow it (or the format cannot be read here): take it from the screen
  }
  const [result] = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: placeOfImage, args: [source] });
  if (!result.result) throw new Error("This picture is not shown on the page, so it cannot be taken. Scroll to it and try again.");
  return shotOf(tab, result.result);
}

async function shotOf(tab, box) {
  const shot = await chrome.tabs.captureVisibleTab(tab.windowId, { format: "png" });
  const bitmap = await createImageBitmap(await (await fetch(shot)).blob());
  const inside = boxOnShot(box, box.viewportWidth, bitmap.width, bitmap.height);
  if (!inside) throw new Error("The box is outside the window.");
  return asPng(await createImageBitmap(bitmap, inside.x, inside.y, inside.width, inside.height));
}

async function asPng(bitmap) {
  const size = storedSize(bitmap.width, bitmap.height);
  const canvas = new OffscreenCanvas(size.width, size.height);
  canvas.getContext("2d").drawImage(bitmap, 0, 0, size.width, size.height);
  return new Uint8Array(await (await canvas.convertToBlob({ type: "image/png" })).arrayBuffer());
}

function base64(bytes) {
  let binary = "";
  for (let at = 0; at < bytes.length; at += 0x8000) binary += String.fromCharCode(...bytes.subarray(at, at + 0x8000));
  return btoa(binary);
}

// --- run inside the page ------------------------------------------------------------------------

// The selection, and the text of its paragraph before and after it, so whole sentences can be found.
function aroundSelection() {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0 || selection.isCollapsed) return null;
  const range = selection.getRangeAt(0);
  const elementOf = (node) => (node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement);
  const blockOf = (node) => {
    let at = elementOf(node);
    while (at && at !== document.body && !/^(block|list-item|table-cell|flow-root)$/.test(getComputedStyle(at).display)) at = at.parentElement;
    return at || document.body;
  };
  const head = document.createRange();
  head.selectNodeContents(blockOf(range.startContainer));
  head.setEnd(range.startContainer, range.startOffset);
  const tail = document.createRange();
  tail.selectNodeContents(blockOf(range.endContainer));
  tail.setStart(range.endContainer, range.endOffset);
  const textOf = (part) => {   // as the reader sees it: a page's <style> inside a paragraph is not text
    const copy = part.cloneContents();
    copy.querySelectorAll("style, script, noscript, template, annotation").forEach((hidden) => hidden.remove());   // annotation: a formula's source
    // each block of the page (a paragraph, a list item, a heading, a line break) ends with a blank line, so
    // "counterparty.</li><li>The" is two sentences, not "counterparty.The"
    copy.querySelectorAll("br").forEach((brk) => brk.replaceWith("\n\n"));
    copy.querySelectorAll("p, div, li, dt, dd, h1, h2, h3, h4, h5, h6, blockquote, pre, tr, td, th, section, article, header, footer, figcaption")
      .forEach((block) => { block.before("\n\n"); block.after("\n\n"); });
    return copy.textContent;
  };
  return { selected: selection.toString(), before: textOf(head), after: textOf(tail) };
}

// Where the image is in the window, once it is scrolled into view.
function placeOfImage(source) {
  const image = [...document.images].find((one) => one.currentSrc === source || one.src === source);
  if (!image || image.getBoundingClientRect().width < 2 || image.getBoundingClientRect().height < 2) return null;   // hidden
  image.scrollIntoView({ block: "center" });
  return new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(() => {
    const r = image.getBoundingClientRect();
    done({ x: r.left, y: r.top, width: r.width, height: r.height, viewportWidth: window.innerWidth });
  })));
}

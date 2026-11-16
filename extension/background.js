// The right-click items. On selected text: make a clip (the browser hands over the selected text itself, so this
// needs no access to the page). On an image or the page: put a picture on the newest card in the side panel; the
// right-click lets the extension see that one tab (activeTab), and nothing else.
import { MENU, NO_CARD_YET, PICTURE_MENU, boxOnShot, clipFor, findSentmine, storedSize } from "./logic.js";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    for (const [id, title] of Object.entries(MENU)) {
      chrome.contextMenus.create({ id, title, contexts: ["selection"] });
    }
    chrome.contextMenus.create({ id: "picture", title: PICTURE_MENU.picture, contexts: ["image"] });
    chrome.contextMenus.create({ id: "part", title: PICTURE_MENU.part, contexts: ["page"] });
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  // The panel must be opened at once, while the click still counts as the reader's own action.
  if (tab && tab.windowId !== undefined) chrome.sidePanel.open({ windowId: tab.windowId }).catch(() => {});
  const work = info.menuItemId in PICTURE_MENU ? addPicture(info, tab) : sendClip(info);
  work.then((news) => chrome.runtime.sendMessage(news).catch(() => {}));   // the panel may still be opening
});

export async function sendClip(info) {
  const clip = clipFor(info.menuItemId, info.selectionText);
  if (clip.refuse) return { clip: "refused", message: clip.refuse };
  const base = await findSentmine(fetch);
  if (!base) return { clip: "no-sentmine" };
  try {
    const response = await fetch(base + "/clip/api/text", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(clip),
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
    png = info.menuItemId === "picture" ? await imagePng(info.srcUrl, tab) : await partPng(tab);
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
  if (!result.result) throw new Error("This picture is not shown on the page, so it cannot be taken. Scroll to it, or drag a box around it.");
  return shotOf(tab, result.result);
}

// A box the reader drags on the page, then what the window shows inside it.
async function partPng(tab) {
  const [result] = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: drawBox });
  return result.result ? shotOf(tab, result.result) : null;
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

// A box the reader drags over the page; Esc or a tiny box gives nothing. The marks are gone before the screenshot.
function drawBox() {
  return new Promise((done) => {
    const cover = document.createElement("div");
    cover.style.cssText = "position:fixed;inset:0;z-index:2147483647;cursor:crosshair;background:rgba(31,35,40,0.12)";
    const frame = document.createElement("div");
    frame.style.cssText = "position:fixed;border:2px solid #1a5fd0;background:rgba(26,95,208,0.12);display:none";
    const hint = document.createElement("div");
    hint.textContent = "Drag a box around the formula or picture. Esc cancels.";
    hint.style.cssText = "position:fixed;top:12px;left:50%;transform:translateX(-50%);padding:6px 12px;border-radius:6px;" +
      "background:#1f2328;color:#f6f5f1;font:14px system-ui,sans-serif";
    cover.append(frame, hint);
    document.documentElement.append(cover);
    let start = null;
    const finish = (box) => {
      cover.remove();
      document.removeEventListener("keydown", key, true);
      requestAnimationFrame(() => requestAnimationFrame(() => done(box)));   // painted without the marks
    };
    const key = (event) => { if (event.key === "Escape") { event.preventDefault(); finish(null); } };
    document.addEventListener("keydown", key, true);
    cover.addEventListener("mousedown", (event) => { event.preventDefault(); start = [event.clientX, event.clientY]; });
    cover.addEventListener("mousemove", (event) => {
      if (!start) return;
      const [x, y] = [Math.min(start[0], event.clientX), Math.min(start[1], event.clientY)];
      Object.assign(frame.style, { display: "block", left: x + "px", top: y + "px",
        width: Math.abs(event.clientX - start[0]) + "px", height: Math.abs(event.clientY - start[1]) + "px" });
    });
    cover.addEventListener("mouseup", (event) => {
      if (!start) return;
      const box = { x: Math.min(start[0], event.clientX), y: Math.min(start[1], event.clientY),
        width: Math.abs(event.clientX - start[0]), height: Math.abs(event.clientY - start[1]), viewportWidth: window.innerWidth };
      finish(box.width < 8 || box.height < 8 ? null : box);
    });
  });
}

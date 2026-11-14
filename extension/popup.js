// Pressing the button opens this panel: it sends the tab to sentmine and shows sentmine's Read page.
import { NOT_RUNNING, findSentmine, whatToSend } from "./logic.js";

const say = (text, warn = false) => {
  const line = document.getElementById("say");
  line.textContent = text;
  line.className = warn ? "warn" : "soft";
};

// Runs inside the page, after vendor/Readability.js (Mozilla's reader-view library): the selected text,
// or the article without the site's menus and side boxes, one paragraph per block; and a Download link,
// for a page about a file.
function readPage() {
  const BLOCKS = "h1,h2,h3,h4,h5,h6,p,li,blockquote,pre,dt,dd";
  // Parts of a page that are not its running text: notes above the article, info and navigation boxes,
  // reference lists, edit links (the names Wikipedia and many other sites use).
  const NOT_TEXT = '[role="note"], [role="navigation"], .hatnote, .infobox, .navbox, .sidebar, .reflist, .references, .mw-editsection, sup.reference, .metadata';
  let text = "";
  try {
    const copy = document.cloneNode(true);
    copy.querySelectorAll(NOT_TEXT).forEach((part) => part.remove());
    const article = new Readability(copy).parse();
    if (article && article.content) {
      const doc = new DOMParser().parseFromString(article.content, "text/html");
      const blocks = [...doc.querySelectorAll(BLOCKS)]
        .filter((block) => !block.querySelector(BLOCKS) && !block.closest("table, figure"));   // not tables or pictures
      const parts = blocks.map((block) => block.textContent.replace(/\s+/g, " ").trim()).filter(Boolean);
      if (article.title && parts[0] !== article.title.trim()) parts.unshift(article.title.trim());
      text = parts.join("\n\n");
    }
  } catch (error) {
    text = "";
  }
  if (text.length < 200) {   // not an article: the page's main text as it is shown
    const main = document.querySelector("article") || document.querySelector("main") || document.body;
    text = main ? main.innerText : "";
  }
  const link = document.querySelector('a[href*="/files/"][href*="/download"]');
  return {
    contentType: document.contentType,
    selection: String(getSelection()),
    text,
    download: link ? link.href : "",
    downloadName: link ? link.textContent.replace(/^\s*Download\s+/i, "").trim() : "",
  };
}

async function pageOf(tab) {
  try {
    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["vendor/Readability.js"] });
    const [result] = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: readPage });
    return result.result;
  } catch (error) {
    return null;   // the browser does not let extensions into this tab (its PDF viewer, for one)
  }
}

// Runs inside the page: downloads a file the way the page itself would, with its login, and hands it over
// as base64 (what can pass from a page to the extension).
async function downloadInPage(url) {
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) return { status: response.status };
  const bytes = new Uint8Array(await response.arrayBuffer());
  let binary = "";
  for (let at = 0; at < bytes.length; at += 0x8000) binary += String.fromCharCode(...bytes.subarray(at, at + 0x8000));
  return { base64: btoa(binary) };
}

async function pdfBlob(tab, what) {
  try {
    const response = await fetch(what.pdf, { credentials: "include" });   // the reader's own login, if the site needs one
    if (response.ok) return await response.blob();
    if (!what.fromPage) throw new Error("status " + response.status);
  } catch (error) {
    if (!what.fromPage) throw new Error("The PDF could not be downloaded again. Save it and use Open a file in sentmine.");
  }
  // A Download link can lead to another address that the extension may not fetch; the page itself can.
  const [result] = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: downloadInPage, args: [what.pdf] });
  const got = result.result || {};
  if (!got.base64) throw new Error("The file could not be downloaded (" + (got.status || "no answer") + "). Download it and use Open a file in sentmine.");
  const binary = atob(got.base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type: "application/pdf" });
}

async function send(base, tab, what) {
  if (what.text !== undefined) {
    return fetch(base + "/api/text", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: what.text }),
    });
  }
  const form = new FormData();
  form.append("file", await pdfBlob(tab, what), what.name);
  return fetch(base + "/api/file", { method: "POST", body: form });
}

async function showRead(base) {
  const [open] = await chrome.tabs.query({ url: base + "/*" });
  if (open) {
    await chrome.tabs.update(open.id, { active: true, url: base + "/" });
    await chrome.windows.update(open.windowId, { focused: true });
  } else {
    await chrome.tabs.create({ url: base + "/" });
  }
}

export async function openInSentmine(tab) {
  const what = whatToSend(tab.url || "", await pageOf(tab));
  if (what.refuse) return say(what.refuse, true);
  const base = await findSentmine(fetch);
  if (!base) return say(NOT_RUNNING, true);
  say(what.pdf ? "Sending " + what.name + "…" : "Sending the page's text…");
  try {
    const response = await send(base, tab, what);
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      return say(data.error || "sentmine could not read it (" + response.status + ").", true);
    }
  } catch (error) {
    return say(error.message, true);
  }
  await showRead(base);
  return "sent";
}

const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

document.getElementById("open").addEventListener("click", async () => {
  if (tab && (await openInSentmine(tab)) === "sent") window.close();
});

document.getElementById("panel").addEventListener("click", async () => {
  if (tab) await chrome.sidePanel.open({ windowId: tab.windowId });   // the click lets the panel open
  window.close();
});

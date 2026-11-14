// Pressing the button opens this panel: it sends the tab to sentmine and shows sentmine's Read page.
import { NOT_RUNNING, findSentmine, pdfName, whatToSend } from "./logic.js";

const say = (text, warn = false) => {
  const line = document.getElementById("say");
  line.textContent = text;
  line.className = warn ? "warn" : "soft";
};

// Runs inside the page: the selected text, or the page's main text.
function readPage() {
  const main = document.querySelector("article") || document.querySelector("main") || document.body;
  return { contentType: document.contentType, selection: String(getSelection()), text: main ? main.innerText : "" };
}

async function pageOf(tab) {
  try {
    const [result] = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: readPage });
    return result.result;
  } catch (error) {
    return null;   // the browser does not let extensions into this tab (its PDF viewer, for one)
  }
}

async function send(base, what) {
  if (what.text !== undefined) {
    return fetch(base + "/api/text", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: what.text }),
    });
  }
  const pdf = await fetch(what.pdf, { credentials: "include" });   // the reader's own login, if the site needs one
  if (!pdf.ok) throw new Error("The PDF could not be downloaded again (" + pdf.status + "). Save it and use Open a file in sentmine.");
  const form = new FormData();
  form.append("file", await pdf.blob(), pdfName(what.pdf));
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
  say(what.pdf ? "Sending the PDF…" : "Sending the page's text…");
  try {
    const response = await send(base, what);
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
if (tab && (await openInSentmine(tab)) === "sent") window.close();

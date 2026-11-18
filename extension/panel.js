// The side panel beside the page: sentmine's own page for the clips (/clip), shown in a frame.
import { EDITING_MENU, MENU, NOT_RUNNING, PICTURE_MENU, findSentmine } from "./logic.js";

// While a card is open in Edit here, the right-click items say that what is chosen goes into it.
function nameMenu(editing) {
  const titles = editing ? EDITING_MENU : { ...MENU, ...PICTURE_MENU };
  for (const [id, title] of Object.entries(titles)) {
    try {
      const done = chrome.contextMenus.update(id, { title });
      if (done && done.catch) done.catch(() => {});
    } catch (error) {
      // the item is not there (yet): nothing to name
    }
  }
}

window.addEventListener("message", (event) => {
  const frameWindow = document.getElementById("clips").contentWindow;
  if (event.source === frameWindow && event.data && event.data.sentmine === "editing") nameMenu(event.data.editing);
});
window.addEventListener("pagehide", () => nameMenu(false));   // the panel closed: the usual names again

const frame = document.getElementById("clips");
const say = document.getElementById("say");
const line = document.getElementById("line");

function tell(text, warn = false) {
  frame.hidden = true;
  say.hidden = false;
  line.textContent = text;
  line.className = warn ? "warn" : "";
}

function show(base) {
  say.hidden = true;
  if (!frame.hidden && frame.dataset.base === base) {
    // sentmine is shown already: it looks for the new clip itself, so a card open in Edit stays open
    frame.contentWindow.postMessage("sentmine:refresh", base);
    return;
  }
  frame.hidden = false;
  frame.dataset.base = base;
  frame.src = base + "/clip?" + Date.now();
}

async function start() {
  const base = await findSentmine(fetch);
  if (base) {
    show(base);
    return;
  }
  tell(NOT_RUNNING, true);
  const again = document.createElement("button");
  again.textContent = "Try again";
  again.addEventListener("click", () => { again.remove(); tell("Looking for sentmine…"); start(); });
  say.append(again);
}

chrome.runtime.onMessage.addListener((news) => {
  if (news.clip === "added") show(news.base);
  else if (news.clip === "no-sentmine") tell(NOT_RUNNING, true);
  else if (news.clip === "refused") tell(news.message, true);
});

start();

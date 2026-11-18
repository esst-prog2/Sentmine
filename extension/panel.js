// The side panel beside the page: sentmine's own page for the clips (/clip), shown in a frame.
import { NOT_RUNNING, findSentmine } from "./logic.js";

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

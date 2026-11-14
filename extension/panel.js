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
  frame.hidden = false;
  frame.src = base + "/clip?" + Date.now();   // a new address, so a new clip is always shown
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

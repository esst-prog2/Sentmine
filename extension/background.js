// The right-click items on selected text. The browser hands over the selected text itself,
// so making a clip needs no access to the page.
import { MENU, clipFor, findSentmine } from "./logic.js";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    for (const [id, title] of Object.entries(MENU)) {
      chrome.contextMenus.create({ id, title, contexts: ["selection"] });
    }
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  // The panel must be opened at once, while the click still counts as the reader's own action.
  if (tab && tab.windowId !== undefined) chrome.sidePanel.open({ windowId: tab.windowId }).catch(() => {});
  sendClip(info).then((news) => chrome.runtime.sendMessage(news).catch(() => {}));   // the panel may still be opening
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

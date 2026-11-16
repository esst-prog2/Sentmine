// What the button decides, kept apart from the browser so it can be tested with node.

export const PORTS = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010];   // as sentmine's free_port()

export const NOT_RUNNING =
  "sentmine is not running. Start it with `sentmine` in a terminal, then press the button again.";

// Asks every port at once who it is; the first port that answers as sentmine wins, so another
// program on port 8000 is never sent anything.
export async function findSentmine(fetchFn, ports = PORTS, wait = 600) {
  const answers = await Promise.all(ports.map(async (port) => {
    const base = "http://127.0.0.1:" + port;
    try {
      const response = await fetchFn(base + "/api/hello", { signal: AbortSignal.timeout(wait) });
      const data = await response.json();
      return data && data.app === "sentmine" ? base : null;
    } catch (error) {
      return null;
    }
  }));
  return answers.find((base) => base !== null) || null;
}

// The right-click items on selected text, by the kind of clip each one makes.
export const MENU = { word: "Word card from this sentence", definition: "Definition card from this" };

// The right-click items that put a picture on the newest card in the side panel.
export const PICTURE_MENU = {
  picture: "Add this picture to the last card",
  part: "Add a part of this page to the last card",
};

export const NO_CARD_YET =
  "Make a card in the side panel first: select a sentence, right-click it, and choose Word card from this sentence.";

export const WIDEST_PICTURE = 1600;   // pixels; a picture wider than this is made smaller, as Anki shows it no wider

// A box drawn on the visible page (CSS pixels of a window `viewportWidth` wide), in the pixels of a screenshot
// of that window, kept inside the screenshot.
export function boxOnShot(box, viewportWidth, shotWidth, shotHeight) {
  const scale = shotWidth / viewportWidth;
  const x = Math.max(0, Math.round(box.x * scale));
  const y = Math.max(0, Math.round(box.y * scale));
  const width = Math.min(shotWidth - x, Math.round(box.width * scale));
  const height = Math.min(shotHeight - y, Math.round(box.height * scale));
  return width > 0 && height > 0 ? { x, y, width, height } : null;
}

// The size a picture is stored at: as it is, or narrowed to WIDEST_PICTURE keeping its shape.
export function storedSize(width, height) {
  if (width <= WIDEST_PICTURE) return { width, height };
  return { width: WIDEST_PICTURE, height: Math.round(height * WIDEST_PICTURE / width) };
}

export const LONGEST_CLIP = 3000;   // characters: a sentence or a definition, not a whole page

// The clip for a right-click item and the selected text, or a reason not to send it.
export function clipFor(menuItemId, selected) {
  if (!(menuItemId in MENU)) return { refuse: "That is not one of sentmine's menu items." };
  const text = tidy(selected || "");
  if (text === "") return { refuse: "Select a sentence or a definition first, then right-click it." };
  if (text.length > LONGEST_CLIP) {
    return { refuse: "That is a lot of text for one card. Select one sentence or one definition, or send the whole page with the sentmine button." };
  }
  return { text, kind: menuItemId };
}

// Marks a web page puts in its text that are not part of it: reference numbers like [12], [edit].
export function tidy(text) {
  return text
    .replace(/\[\s*(\d+|[a-z]|edit|citation needed|note \d+)\s*\]/gi, "")
    .replace(/[ \t]+([.,;:])/g, "$1")
    .replace(/[ \t]{2,}/g, " ")
    .trim();
}

const isCanvasFilePage = (address) =>
  /\/files\/\d+/.test(address.pathname) && /instructure|canvas/i.test(address.hostname);

// What to send for a tab: a PDF to fetch, a text, or a reason not to send anything.
// `page` is what the page itself said: { contentType, selection, text, download, downloadName };
// it is null when the browser does not let the extension read the tab, as in its built-in PDF viewer.
export function whatToSend(url, page) {
  let address;
  try {
    address = new URL(url);
  } catch (error) {
    return { refuse: "This tab has no address sentmine can open." };
  }
  if (address.protocol === "file:") {
    return { refuse: "This is a file on your computer: open it in sentmine with Open a file." };
  }
  if (address.protocol !== "http:" && address.protocol !== "https:") {
    return { refuse: "This is one of the browser's own pages. Open a web page or a PDF, then press the button." };
  }
  if (address.hostname === "127.0.0.1" || address.hostname === "localhost") {
    return { refuse: "This is already sentmine (or another app on this computer)." };
  }
  const isPdf = address.pathname.toLowerCase().endsWith(".pdf") || page === null || page.contentType === "application/pdf";
  if (isPdf) return { pdf: url, name: pdfName(url) };
  if (isCanvasFilePage(address)) {
    // Canvas's page about a file: its Download link gives the file, with the reader's own login.
    if (page.download) return { pdf: page.download, name: pdfName(page.download, page.downloadName), fromPage: true };
    return { refuse: "This Canvas page has no Download link. Download the file, then open it in sentmine with Open a file." };
  }
  const chosen = tidy(page.selection.trim() !== "" ? page.selection : page.text);
  if (chosen === "") return { refuse: "This page has no text sentmine can read." };
  return { text: chosen };
}

// The file name sentmine is told (sentmine reads a PDF by its name's ending): the name the page gives,
// or the last part of the address.
export function pdfName(url, given = "") {
  const last = given.trim() || decodeURIComponent(new URL(url).pathname.split("/").pop() || "");
  return last.toLowerCase().endsWith(".pdf") ? last : (last || "page") + ".pdf";
}

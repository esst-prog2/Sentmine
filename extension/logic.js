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

// What to send for a tab: a PDF to fetch, a text, or a reason not to send anything.
// `page` is what the page itself said; it is null when the browser does not let the extension
// read the tab, as in its built-in PDF viewer.
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
  if (isPdf) return { pdf: url };
  if (/\/files\/\d+/.test(address.pathname) && /instructure|canvas/i.test(address.hostname)) {
    return { refuse: "This is Canvas's page about a file. Open the PDF itself (Download, or open it in its own tab), then press the button again." };
  }
  const chosen = page.selection.trim() !== "" ? page.selection : page.text;
  if (chosen.trim() === "") return { refuse: "This page has no text sentmine can read." };
  return { text: chosen };
}

// The file name sentmine is told, from the address (sentmine reads a PDF by its name's ending).
export function pdfName(url) {
  const last = decodeURIComponent(new URL(url).pathname.split("/").pop() || "");
  return last.toLowerCase().endsWith(".pdf") ? last : (last || "page") + ".pdf";
}

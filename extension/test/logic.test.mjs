import assert from "node:assert/strict";
import { test } from "node:test";
import { findSentmine, pdfName, tidy, whatToSend } from "../logic.js";

const page = (text, selection = "", contentType = "text/html", download = "", downloadName = "") =>
  ({ text, selection, contentType, download, downloadName });

test("a web page sends its text", () => {
  assert.deepEqual(whatToSend("https://example.org/article", page("Outliers can skew it.")), { text: "Outliers can skew it." });
});

test("a selection wins over the page", () => {
  assert.deepEqual(whatToSend("https://example.org/a", page("All of it.", "Just this.")), { text: "Just this." });
});

test("reference marks are taken out of the text", () => {
  assert.equal(tidy("It is the oldest award.[1] It was held in 1929.[6][edit] See [a] above."),
    "It is the oldest award. It was held in 1929. See above.");
  assert.deepEqual(whatToSend("https://en.wikipedia.org/wiki/X", page("In film.[1][2] Then.")), { text: "In film. Then." });
});

test("a PDF is sent as a file: by its ending, by its type, or when the page cannot be read", () => {
  assert.deepEqual(whatToSend("https://example.org/book.PDF", page("x")), { pdf: "https://example.org/book.PDF", name: "book.PDF" });
  assert.deepEqual(whatToSend("https://example.org/get?id=3", page("", "", "application/pdf")), { pdf: "https://example.org/get?id=3", name: "get.pdf" });
  assert.deepEqual(whatToSend("https://example.org/viewer", null), { pdf: "https://example.org/viewer", name: "viewer.pdf" });
});

test("Canvas's page about a file sends the file behind its Download link", () => {
  const link = "https://canvas.elte.hu/courses/1/files/42/download?download_frd=1";
  assert.deepEqual(
    whatToSend("https://canvas.elte.hu/courses/1/files/42", page("menu", "", "text/html", link, "01 Public Policy - Intro.pdf")),
    { pdf: link, name: "01 Public Policy - Intro.pdf", fromPage: true });
  assert.match(whatToSend("https://elte.instructure.com/courses/1/files/42?module_item_id=9", page("menu")).refuse, /no Download link/);
});

test("tabs it cannot read say what to do instead", () => {
  assert.match(whatToSend("file:///C:/book.pdf", null).refuse, /Open a file/);
  assert.match(whatToSend("edge://settings", null).refuse, /browser's own pages/);
  assert.match(whatToSend("http://127.0.0.1:8000/", page("x")).refuse, /already sentmine/);
  assert.match(whatToSend("https://example.org/empty", page("   ")).refuse, /no text/);
});

test("the PDF keeps its name, or gets one", () => {
  assert.equal(pdfName("https://example.org/files/Causal%20Primer.pdf"), "Causal Primer.pdf");
  assert.equal(pdfName("https://example.org/get"), "get.pdf");
  assert.equal(pdfName("https://canvas.example/files/42/download", "Slides"), "Slides.pdf");
});

function fakeFetch(answers) {
  return async (url) => {
    const port = Number(new URL(url).port);
    if (!(port in answers)) throw new Error("nothing listens");
    return { json: async () => answers[port] };
  };
}

test("sentmine is found by its answer, not by its port", async () => {
  assert.equal(await findSentmine(fakeFetch({ 8000: { app: "something else" }, 8001: { app: "sentmine" } })), "http://127.0.0.1:8001");
  assert.equal(await findSentmine(fakeFetch({ 8003: { app: "sentmine" }, 8005: { app: "sentmine" } })), "http://127.0.0.1:8003");
  assert.equal(await findSentmine(fakeFetch({})), null);
});

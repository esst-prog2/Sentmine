import assert from "node:assert/strict";
import { test } from "node:test";
import { findSentmine, pdfName, whatToSend } from "../logic.js";

const page = (text, selection = "", contentType = "text/html") => ({ text, selection, contentType });

test("a web page sends its main text", () => {
  assert.deepEqual(whatToSend("https://example.org/article", page("Outliers can skew it.")), { text: "Outliers can skew it." });
});

test("a selection wins over the page", () => {
  assert.deepEqual(whatToSend("https://example.org/a", page("All of it.", "Just this.")), { text: "Just this." });
});

test("a PDF is sent as a file: by its ending, by its type, or when the page cannot be read", () => {
  assert.deepEqual(whatToSend("https://example.org/book.PDF", page("x")), { pdf: "https://example.org/book.PDF" });
  assert.deepEqual(whatToSend("https://example.org/get?id=3", page("", "", "application/pdf")), { pdf: "https://example.org/get?id=3" });
  assert.deepEqual(whatToSend("https://example.org/viewer", null), { pdf: "https://example.org/viewer" });
});

test("tabs it cannot read say what to do instead", () => {
  assert.match(whatToSend("file:///C:/book.pdf", null).refuse, /Open a file/);
  assert.match(whatToSend("edge://settings", null).refuse, /browser's own pages/);
  assert.match(whatToSend("http://127.0.0.1:8000/", page("x")).refuse, /already sentmine/);
  assert.match(whatToSend("https://canvas.elte.hu/courses/1/files/42", page("menu")).refuse, /PDF itself/);
  assert.match(whatToSend("https://elte.instructure.com/courses/1/files/42?module_item_id=9", page("menu")).refuse, /PDF itself/);
  assert.match(whatToSend("https://example.org/empty", page("   ")).refuse, /no text/);
});

test("the PDF keeps its name, or gets one", () => {
  assert.equal(pdfName("https://example.org/files/Causal%20Primer.pdf"), "Causal Primer.pdf");
  assert.equal(pdfName("https://example.org/get"), "get.pdf");
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

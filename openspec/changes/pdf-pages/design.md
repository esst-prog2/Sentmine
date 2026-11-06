## Context

`document.read_pdf` turns a PDF into clean text: running heads and page numbers dropped, words broken at line ends rejoined, lines joined into paragraphs. The reading page draws that text as words (`.w` spans with a sentence and word number) and every card is made from those numbers. A PDF shown as pages must keep those numbers, or cards, picked words and duplicates would need a second set of rules.

## Goals / Non-Goals

**Goals:** the real pages; every pick works as on a pasted text; a long book opens in seconds.

**Non-Goals:** a full PDF viewer (zoom, outline, links, search); scanned PDFs; editing the PDF.

## Decisions

**Pictures from pdfium and boxes from sentmine, not PDF.js.** PDF.js would draw the pages, but its text layer knows nothing of sentmine's sentences and words. pdfium already reads the text and knows where each character is. The server draws each page as a PNG (1600 px wide, written with `zlib`, so no new dependency) and sends the boxes of the words on that page as fractions of the page, so they fit any width.

**Finding the text's words among the page's characters.** The clean text and the characters on the pages differ: running heads are gone, broken words are joined, and `𝑋` is one character but two UTF-16 halves in pdfium. Both sides are turned into runs of letters (NFKC, ignoring case; digits and punctuation end a run, as they end a word) and matched in order with `difflib.SequenceMatcher`, 1500 runs at a time, so the time grows with the length of the book. Runs that are the same letters cut differently, such as `consid` `erably` against `considerably`, are matched letter by letter. A lone match of fewer than three runs does not move the place in the pages, so a `the` found far ahead is not followed.

A first, greedy version that searched forward for each word lost its place in tables (digits between words) and in repeated text (a question and its solution); the matcher above replaced it. Measured on four real PDFs of 75, 26, 10 and 166 pages: 99.9 to 100% of words placed, in 0.5 to 5.9 s.

**A word on two lines has two boxes** with the same sentence and word number, so either half can be clicked.

**A drag over boxes is read from the words, not from the browser.** The boxes are separate, so the browser's selection text has no spaces or paragraph breaks. The page takes the first and last word box selected and rebuilds the passage from the words of the text between them, with the punctuation right after the last word.

**Pages and boxes are made when they come near the screen.** Pictures use `loading="lazy"`; the boxes of a page are fetched when it is within 1200 px of the screen. Pages are drawn once per PDF; later answers only update which words are picked.

**One lock around pdfium.** pdfium is not safe to use from two threads, and the browser asks for several pictures at once. Without the lock, drawing a page failed with "Data format error", and in a test parallel use crashed Python. The open document is kept, to draw pages without opening the file again.

**The address of a picture carries the PDF's version,** so a picture of an earlier PDF is never taken from the browser's cache.

## Risks / Trade-offs

- [A word not found has no box and cannot be clicked] -> Rare in the PDFs measured; it is still part of a passage dragged across it, since the passage comes from the text.
- [A rotated page] -> Not handled and not tested.
- [Memory: the open PDF is kept] -> At most 50 MB, the largest file accepted.
- [Formulas] -> Letters inside formulas are words of the text and get boxes; symbols do not.

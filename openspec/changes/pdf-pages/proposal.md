## Why

A PDF opened in sentmine is shown as plain extracted text: its layout, headings, tables and formulas are gone, and some lines come out with glued words. The reader wants to read the book as it looks and still pick words and definitions from it. This is the first step towards reading in place; a browser extension for web pages may follow.

## What Changes

- A PDF opened on the reading page is shown as its own pages, one picture per page, drawn by pdfium (already used to read PDFs).
- Each word of the text read from the PDF gets an invisible box over the place it is printed, so a click on a printed word and a drag over printed text work as on a pasted text: word cards, definition cards, picked words, the earlier-card check, cloze.
- Pages are drawn and their words placed only when they come near the screen, so a long book opens quickly.
- While reading a long PDF, the status line and the cards panel stay in view.
- A pasted text and a .txt file are shown as before.

Not in this change: zoom; choosing pages; scanned PDFs; a PDF's links and outline; web pages (a browser extension is a later change).

## Capabilities

### New Capabilities
- `pdf-pages`: showing a PDF as its pages, finding each word of its text on them, and picking from the pages.

### Modified Capabilities

None. Word and definition cards keep their rules; on a PDF they are picked from the pages.

## Impact

- New `pages.py`: word boxes and page pictures. `document.py`: one lock around every use of pdfium.
- `app.py`: `pdf` in the page state; `GET /api/pages/<n>/words` and `GET /api/pages/<n>.png`.
- `web/index.html`: drawing pages, reading a drag over boxes, the status line and cards staying in view.

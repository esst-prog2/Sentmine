## 1. Finding words on pages

- [x] 1.1 `pages.locate`: runs of letters on both sides, matched in chunks; broken words letter by letter; boxes per line as fractions of the page; verify with hand-made PDFs and by measuring four real PDFs
- [x] 1.2 `pages.picture`: a page as a PNG written with zlib; one lock around every use of pdfium; verify drawing and reading in parallel

## 2. The app

- [x] 2.1 `pdf` in the state, `/api/pages/<n>/words`, `/api/pages/<n>.png`; a pasted text or .txt clears it; verify with the test client

## 3. The page

- [x] 3.1 Draw pages lazily, place boxes, mark picked words, read a drag over boxes from the text; the status line and cards stay in view; verify clicks and drags on Pearl's manual in headless Edge, and the 12 checks on pasted text
- [x] 3.2 Screenshots light and dark, at full and phone width

## 4. Wrap-up

- [x] 4.1 Run the whole suite and `openspec validate pdf-pages --strict`
- [ ] 4.2 The reader opens one of their PDFs and makes word and definition cards from its pages (needs the reader)

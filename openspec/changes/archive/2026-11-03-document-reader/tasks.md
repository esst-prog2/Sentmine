## 1. Cleaning

- [x] 1.1 Write `document.clean_pages(pages)` with the rules of "Cleaning the text of a PDF"; verify a test with text invented by hand for each scenario

## 2. Reading files

- [x] 2.1 Add `pypdfium2==5.14.0`; write `tests/pdf_helper.py`, `read_pdf(data)` and `read_file(name, data)`; verify tests for "A PDF with text", "A text file" and each case of "Files that cannot be read"

## 3. The app and the page

- [x] 3.1 `POST /api/file` with a 50 MB limit, returning the state and the page count; verify with the test client, including that a refused file leaves the text and cards as they are
- [x] 3.2 A file button on the reading page that asks before replacing cards; verify the script has no syntax error

## 4. Wrap-up

- [x] 4.1 Run the whole suite and `openspec validate document-reader --strict`; verify both pass and the first design still writes 103 cards
- [x] 4.2 Load the real 42-page PDF through the code; verify the running heads are gone, hyphenated words are rejoined, and measure how long a click takes on the server
- [x] 4.3 Try it in the browser with a real PDF: load, pick a word, Suggest meaning, download (needs the reader)

  Done by the reader on 2026-11-03: the 42-page PDF loaded in the browser and the spaces are right on the pages that were glued before (the reader's report). Picking a word, Suggest meaning and Download on a loaded PDF share their code with pasted text, are covered by tests, and were not reported separately.

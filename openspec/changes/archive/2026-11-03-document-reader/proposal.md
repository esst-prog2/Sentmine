## Why

To read a course document in the app I have to open it, select the text, copy it and paste it, and the pasted text keeps every broken line and running head. The speed test in Homework 5 counted that paste as the app's fixed cost. The professor suggested replacing copy and paste with a reader for documents. Most of what I read for my thesis and courses is PDF.

## What Changes

- The reading page gets a file button: choosing a PDF or `.txt` file loads its text onto the page, in place of pasting. Pasting still works.
- PDF text is cleaned with plain rules: running heads and page numbers are removed, words hyphenated at a line end are rejoined, paragraphs are found, and a sentence is carried across a page break.
- A PDF with no text in it (a scan), a locked PDF, and a file that is not a PDF are refused with a message saying so.
- The message after loading says how many pages were read and how many had no text.
- The file is read on the reader's computer and is not kept or sent anywhere. Word cards, definition cards, AI meanings and My cards work on it as on pasted text.
- New dependency: `pypdfium2`.

Not in this change: scanned pages read by AI; PowerPoint slides; showing the original PDF page; recognising formulas and tables; choosing a page range.

## Capabilities

### New Capabilities
- `document-reader`: loading a PDF or text file, the clean-up rules, and what happens with a file that cannot be read.

### Modified Capabilities

None. Loading replaces the text and cards as pasting does.

## Impact

- New: `src/sentmine/document.py`; a route `POST /api/file`; a file button in `web/index.html`; `tests/pdf_helper.py`, which builds small PDFs for tests.
- `pyproject.toml`: adds `pypdfium2==5.14.0`, and `pypdf==6.21.4` for tests only.
- The reader's books are copyrighted, so no real PDF goes into the repository.

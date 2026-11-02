## Context

The session takes plain text in `Session.load`; everything after that is shared. So a document only has to become clean plain text. The real test file is 42 pages of *Causal Inference in Statistics: A Primer*, with formulas, tables, figures and running heads. Decisions and measurements are in `PLANNING_LOG.md`, 2026-11-02.

## Goals / Non-Goals

**Goals:** a real PDF readable in one step; plain, testable clean-up rules; clear refusals.

**Non-Goals:** recognising formulas, tables or columns; scans; keeping the page layout.

## Decisions

**`document.py` has two parts.** `clean_pages(pages)` takes the text of each page and returns clean text; it knows nothing about PDFs, so its rules are tested with text invented by hand. `read_pdf(data)` calls `pypdfium2` and hands the pages over. `read_file(name, data)` chooses by file extension.

**pypdfium2, chosen by measuring.** On the real file, pypdf glued the words together on 9 of 42 pages, seen by the reader in the browser, and pdfplumber lost spaces too. pypdfium2 and pdfminer glued nothing; pypdfium2 is about 19 times faster than pdfminer, needs no other package and opens empty-password PDFs by itself. Words glued together are counted as lower-case words of 16 letters or more.

**Repeated lines are found by comparing pages.** A line near the top or bottom of a page, with digits removed, counts as a running head if at least three pages have it. Comparing pages needs no knowledge of the book, and it also catches the stray `k k` marks at the top of every page of this file.

**Paragraphs from line length.** PDF text has line breaks but no paragraphs. A line that ends a sentence and is shorter than 85% of the page's median line is taken as a paragraph's end. It can be wrong on short pages; a wrong break only starts a new paragraph, and a sentence never ends earlier than its full stop.

**Reuse `tidy`.** The result is paragraphs separated by blank lines, which `Session.load` already understands.

**Upload with `FormData`, limit 50 MB.** The page posts the file to `POST /api/file`. Flask's `MAX_CONTENT_LENGTH` enforces the limit. The bytes are read in memory and dropped.

**Tests build their own PDFs.** `tests/pdf_helper.py` writes a tiny valid PDF by hand, so no copyrighted file and no extra package is needed. The real file is tried by hand, and the numbers are logged.

## Risks / Trade-offs

- [Formulas and figure labels come out as broken lines inside the text] -> Accepted. They are visible on the page and a card's front can be edited. Telling them from prose needs more than rules.
- [A sentence next to a formula or table runs on, so a card's front is long] -> The preview can shorten it.
- [A long document makes every click redraw thousands of words] -> Measured on the real file as part of the wrap-up; if it is too slow, sending only the changed cards is the fix.
- [A two-column PDF comes out in the wrong order] -> Not handled; the page shows it, and pasting still works.

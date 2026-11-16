## Why

A PDF's own links (its table of contents, references such as "Study question 1.2.3" or "Figure 1.8", web addresses) did nothing in sentmine, because a page is shown as a picture with sentmine's word boxes over it; and there was no way to jump through a long PDF (the critique, 2026-11-14). The reader asked whether those links could work (2026-11-17).

## What Changes

- sentmine reads each page's links from the PDF: a link inside the PDF goes to its page (and the place on it, when the PDF says); a link to a website opens in a new tab (only http, https and mailto). A press on a link follows it and makes no card.
- A page bar at the bottom of the reading area while a PDF is open: the page in view, a page number to jump to, and *Contents* when the PDF has bookmarks.

## Capabilities

### New Capabilities
- `pdf-links`: following a PDF's links and bookmarks, and jumping to a page.

### Modified Capabilities

None.

## Impact

- `pages.py`: the links of each page and the PDF's bookmarks, read with pdfium.
- `app.py`: a page's links come with its words; the bookmarks with the PDF.
- `web/index.html`: the links on each page, the page bar and Contents.

## Why

Going between Read and My cards does not feel smooth (raised by the reader on 2026-11-14 and kept for later; asked for now). Measured frame by frame in headless Edge on the 75-page solution manual, coming back to Read from My cards: for about 190 ms the page shows only its header and an empty reading area, then the whole PDF appears at once on the kept page, and the underlines of words with cards appear about 60 ms after that. My cards also starts empty and fills a moment later. Each page is a full page load that asks the app for its content only after it has opened.

## What Changes

- The app sends each page with its content inside: Read with the reading state, My cards with the first list of cards. The page is drawn complete, on the kept place, in its first frame; it still asks the app as before if that content is missing.
- Going between the two pages fades the content (0.15 s) while the header stays still, in browsers that can (Edge and Chrome); others switch as before. No fade when the system asks for reduced motion.
- The words of each PDF page are cached by the browser like its picture, under the PDF's fingerprint, so the underlines come back at once.

## Capabilities

### New Capabilities
- `page-switch`: going between Read and My cards without an empty page or a jump.

### Modified Capabilities

None.

## Impact

- `app.py`: `/` and `/cards` put their first data into the page; the words of a PDF page can be cached when asked for with the PDF's version.
- `web/index.html`, `web/cards.html`: draw from the data in the page when it is there; the fade between pages; the words asked for with the version.

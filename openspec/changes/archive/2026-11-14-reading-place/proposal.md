## Why

The reader goes from Read to My cards and back to look up a card. Coming back with the Read link starts the text at the top again: on a PDF that was open on page 40 they land on page 1 and have to find their place (checked in headless Edge: page 40 before, page 1 after; only the browser's Back button kept the place). The reader asked for the place to be kept.

## What Changes

- The reading page remembers, in the browser tab, where the reader is in the text: for a PDF the page and how far down it, for pasted text how far down the page.
- Coming back to Read, by the link or by reloading, the page scrolls to that place when the text is the same one.
- A different text, or the same one read again from the paste box or file chooser, starts at the top as before.
- Nothing is saved on disk or on the server for this; a closed tab forgets it.

## Capabilities

### New Capabilities
- `reading-place`: keeping the reader's place in a text when they leave Read and come back.

### Modified Capabilities

None.

## Impact

- `app.py`: the state names the text being read (the text id from met-again).
- `web/index.html`: save the place while scrolling; restore it once, when the page is opened.

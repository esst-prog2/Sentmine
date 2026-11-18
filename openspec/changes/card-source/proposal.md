## Why

A card said where it came from only while it was in the deck; after sending, neither Anki nor My cards knew, so the passage could not be found again. With one deck in two views, the views also showed different cards until the reader acted in each (seen by the reader, 2026-11-17). The reader asked for the source on the card and a little tracking in My cards, and agreed to stop adding features after this.

## What Changes

- Every card keeps its source: a PDF's file name and page, or a web page's title and address. It is shown in the deck, written as a small line on the back of the Anki card, and kept in the card memory (layout 4; a copy of the memory is kept before the change).
- My cards shows each card's source (a web page's title links to it) and the sources most cards came from.
- Read and the side panel notice within about two seconds when the other changed the deck, and draw it again, without interrupting an edit or a drag.

## Capabilities

### New Capabilities
- `card-source`: where a card came from, kept with the card; the views of the one deck kept in step.

### Modified Capabilities

None.

## Impact

- `history.py`, `memory.py`: three source fields; layout 4.
- `reading.py`, `app.py`: the source on each card and note; a deck fingerprint.
- `web/index.html`, `web/cards.html`, `extension/background.js`.

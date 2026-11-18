## Why

Cards from the text in Read and from web pages (the side panel) were two decks, each with its own Download and Send to Anki, so a picture from a web page could not reach a card made from the PDF, and the reader had two lists to keep apart. The reader asked for one deck shown in both places (2026-11-17).

## What Changes

- One deck: the Cards list in Read and in the side panel is the same; Download and Send to Anki take all of it.
- Each card says where it came from (the PDF's name, a pasted text, a web page); each text marks only its own cards' words.
- The texts stay apart: a clip never changes the text in Read; reading a new text in Read removes only the cards from the old text in Read, and asks first.
- *Pictures go here* and *Add a picture* work on any card, so a web picture can go to a card from the PDF and a part of the PDF to a card from the web.

## Capabilities

### New Capabilities
- `one-deck`: one list of cards for the text in Read and the clips from web pages.

### Modified Capabilities

None.

## Impact

- `reading.py`: a `Deck` shared by the two sessions; cards carry their source, origin and text.
- `app.py`: the clip session uses Read's deck; cards in the state carry their origin.
- `web/index.html`: the origin on each card; *Pictures go here* in Read too; the warning before a new text counts only Read's cards.

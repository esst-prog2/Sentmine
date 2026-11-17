## Why

Course books carry much of their meaning in formulas and graphs, and those do not survive as text: a card made from a sentence with a formula, or the definition of a term shown in a graph, loses the part that matters. The reader asked to put formulas and graphs on cards (2026-11-16; planned next on the promo page).

## What Changes

- While a PDF is open, each card in the Cards panel has **Add a picture**. The reader drags a box around a formula or graph on the page; sentmine cuts that part out of the PDF, drawn sharp from the PDF itself, and puts it on the back of the card, under the answer. Esc cancels; the picture can be removed from the card.
- A cloze card shows the picture after the answer (its Back Extra field).
- On a web page, a right-click item on an image, *Add this picture to the chosen card*, puts it on the chosen card (a new card is chosen by itself; *Pictures go here* chooses another). Dragging a box on a web page and *Picture only on the back* were built and then removed on 2026-11-17, to keep the app simple.

## Capabilities

### New Capabilities
- `card-pictures`: a part of a PDF page, such as a formula or graph, on the back of a card.

### Modified Capabilities

None.

## Impact

- `pages.py`: draw a box of a page as a PNG.
- `reading.py`: a card holds its pictures; its back and its note include them.
- `deck.py`, `anki.py`: notes carry media; the deck file and AnkiConnect get them.
- `app.py`: add and remove a picture; serve a card's picture.
- `web/index.html`: the button, drawing the box on the page, the picture on the card.
- Not in this version: pictures on web pages (formulas there are LaTeX, a later step), pictures in My cards (it keeps showing the text).

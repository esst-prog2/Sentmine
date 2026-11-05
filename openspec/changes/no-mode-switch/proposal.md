## Why

The reading page has a Word / Definition switch, and what a click or a drag does depends on it. Reading a text, the reader keeps switching between the two, and a pick in the wrong mode does nothing. A click and a drag are already different gestures, so the page can tell them apart without a switch.

## What Changes

- The Word / Definition switch is removed from the reading page.
- A click on a word makes or removes a word card, as in Word mode today.
- A drag over the text chooses a term; the next drag marks its definition and makes a definition card, as in Definition mode today.
- While a term is waiting, the status line names it and offers Cancel; Esc also cancels it, and a click on a word cancels it before making the word card.
- A double-click or triple-click acts as a click and does not choose a term, because a browser selects a word on double-click.

Not in this change: picking with the keyboard; choosing the passage first and the term second.

## Capabilities

### New Capabilities

None.

### Modified Capabilities
- `reading-app`: "Word cards" and "Definition cards" no longer depend on a mode; a new requirement says how a click and a drag are told apart.

## Impact

- `web/index.html` only: the switch, its styles and hints, and the click and drag handlers. The server, the routes and the cards do not change.
- README section 1 still describes the two modes; it is rewritten for Homework 8, which will describe the page without them.

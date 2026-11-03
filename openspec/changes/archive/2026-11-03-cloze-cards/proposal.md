## Why

A definition card today asks "standard deviation?" and shows the whole passage as the answer. For course concepts, a cloze card is often better: it shows the passage with the term hidden ("The [...] measures how spread out a set of values is.") and asks for the term, so the reader recalls it in context. The passage is already marked when a definition card is made, so a cloze card needs no extra step.

## What Changes

- Each definition card in the preview gets a switch between cloze and term → passage.
- A new definition card starts as cloze when its term appears in its passage, and as term → passage when it does not.
- A cloze card hides every place the term appears in the passage, matching whole words and ignoring case.
- The preview shows a cloze card as Anki will: the front with `[...]`, the back with the term in bold.
- Download and Send to Anki write cloze cards with a second note type, "sentmine: cloze", which Anki treats as a cloze note type. Word cards and term → passage cards are unchanged.
- If an edit takes the term out of the passage, the card becomes term → passage.
- My cards and the memory keep the term and the passage, as for any definition card, so finding an earlier card works as before.

Not in this change: cloze for word cards; more than one hidden part per card (`c2`, `c3`); hiding words other than the term.

## Capabilities

### New Capabilities
- `cloze-cards`: when a definition card is a cloze card, what it hides, the switch, and how it is written to Anki.

### Modified Capabilities

None. Definition cards, Download, Send to Anki and the memory keep their rules; a cloze card is a definition card written differently.

## Impact

- `deck.py`: a second note type and a `Note` that says which type it is. `anki.py`: makes either note type when missing, and finds duplicates across both.
- `reading.py`: a `cloze` flag on cards; `app.py`: `PUT /api/cards/<id>/cloze`; the switch in `web/index.html`.

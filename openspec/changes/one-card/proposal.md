## Why

The reader asked why word cards and definition cards are made in different ways when, after a selection, the text is treated the same (2026-11-18). Two right-click items, two card shapes and two kinds of clip made the app harder to explain than what it does. Selecting a whole sentence exactly on a web page is also slow; a rough selection should be enough.

## What Changes

- **One shape of card**: the term on the front, the passage on the back with the term in bold. A word card is the word (with its base form when it differs) on the front and its sentence on the back. Every card starts as term → passage; *Make it cloze* hides the term, on any card whose term is in its passage.
- The kind stays inside the card (a word is found again by its base form, a term as written), so the memory, the known-word marks and *Made before* work as before. Cards remembered earlier, with the sentence on the front, still show as they were.
- *Suggest meaning* puts the meaning under the passage and replaces the one it put there before.
- **One right-click item**, *Make a card from this*. sentmine takes the whole sentences the selection touches, with the paragraph around it that the extension reads from the tab at that moment. One selected word makes its card at once; a selection with a term in bold makes that term's card at once; anything else waits in the panel as a clip, where a click on a word or a drag over the term makes the card.
- In Read, the passage dragged for a definition is taken as the whole sentences it touches.

## Capabilities

### New Capabilities
- `one-card`: one shape for every card; a rough selection taken as whole sentences.

### Modified Capabilities
- `clip-panel`: one right-click item instead of two; the clip may make its card at once.
- `cloze-cards`: every card can be cloze; a new card starts as term → passage.
- `reading-app`: a word card has the word on the front and its sentence on the back.

## Impact

- `reading.py`: the card's shape, `whole_sentences`, `Session.add_clip`, cloze and Suggest meaning for every card, the old layout in `entry_card`.
- `app.py`: `/clip/api/text` takes the text around the selection and a bold term; the state says whether it is the panel.
- `web/index.html`: one label for every card, cloze offered on every card, one kind of clip.
- `extension/`: one menu item; the paragraph around the selection and a bold term read from the tab (activeTab, at the right-click).
- README, the promo page, tests.

## MODIFIED Requirements

### Requirement: Right-click on selected text
The extension SHALL add one item to the menu of selected text on a web page: "Make a card from this". Choosing it SHALL open the side panel and send sentmine the selection, the text of its paragraph before and after it, and the first phrase in bold inside it, read from that tab only at that moment. sentmine SHALL take the whole sentences the selection touches as a clip. When the selection is one word, the card for that word SHALL be made at once from its sentence; when the selection is two to eight words inside one sentence, and not the whole sentence, the card for those words as a term SHALL be made at once from that sentence; when the selection holds a phrase in bold that is in the clip, the card for that phrase SHALL be made at once with the clip as its passage; otherwise a card SHALL be made at once with the clip as its passage and no term, and SHALL open in Edit in the side panel with the cursor in its Term. While the cursor is in the Term, text right-clicked on the page SHALL go into it exactly as selected, not as whole sentences. Cancel on such a card SHALL delete it, and a deck SHALL NOT be made while a card has no term; a term given in Edit SHALL give the card its key, refused when another card already has that term. When the browser does not let the extension read the tab, the selection alone SHALL be sent. When sentmine is not running, the panel SHALL say so and how to start it.

#### Scenario: One word on a web page
- **WHEN** the reader double-clicks `discrete` on a web page and chooses "Make a card from this"
- **THEN** a card is made at once with `discrete` on the front and its whole sentence on the back

#### Scenario: A definition with its term in bold
- **WHEN** the reader selects, roughly, the first sentence of a Wikipedia article whose term is in bold, and chooses the item
- **THEN** a card is made at once for that term, with the whole sentence as its passage

#### Scenario: A sentence on a web page
- **WHEN** the reader selects the end of one sentence and the start of the next, with no bold phrase, and chooses the item
- **THEN** a card is made with both whole sentences as its passage, and the side panel opens it in Edit with the cursor in its empty Term

#### Scenario: Giving it its term
- **WHEN** the reader then selects `probability distribution` on the page and right-clicks it, and presses Save
- **THEN** the card's term is `probability distribution`

#### Scenario: sentmine is not running
- **WHEN** the reader chooses the item and no sentmine answers
- **THEN** the panel says that sentmine is not running and to start it with `sentmine` in a terminal

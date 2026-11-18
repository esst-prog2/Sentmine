## MODIFIED Requirements

### Requirement: Right-click on selected text
The extension SHALL add one item to the menu of selected text on a web page: "Make a card from this". Choosing it SHALL open the side panel and send sentmine the selection, the text of its paragraph before and after it, and the first phrase in bold inside it, read from that tab only at that moment. sentmine SHALL take the whole sentences the selection touches as a clip. When the selection is one word, the card for that word SHALL be made at once from its sentence; when the selection holds a phrase in bold that is in the clip, the card for that phrase SHALL be made at once with the clip as its passage; otherwise the clip SHALL wait in the panel. When the browser does not let the extension read the tab, the selection alone SHALL be sent. When sentmine is not running, the panel SHALL say so and how to start it.

#### Scenario: One word on a web page
- **WHEN** the reader double-clicks `discrete` on a web page and chooses "Make a card from this"
- **THEN** a card is made at once with `discrete` on the front and its whole sentence on the back

#### Scenario: A definition with its term in bold
- **WHEN** the reader selects, roughly, the first sentence of a Wikipedia article whose term is in bold, and chooses the item
- **THEN** a card is made at once for that term, with the whole sentence as its passage

#### Scenario: A sentence on a web page
- **WHEN** the reader selects part of a sentence with no bold phrase and chooses the item
- **THEN** the side panel shows the whole sentence with its words clickable, and no card is made yet

#### Scenario: sentmine is not running
- **WHEN** the reader chooses the item and no sentmine answers
- **THEN** the panel says that sentmine is not running and to start it with `sentmine` in a terminal

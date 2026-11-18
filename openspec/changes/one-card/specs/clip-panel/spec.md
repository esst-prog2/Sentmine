## MODIFIED Requirements

### Requirement: Right-click on selected text
The extension SHALL add one item to the menu of selected text on a web page: "Make a card from this". Choosing it SHALL open the side panel and send sentmine the selection and the text of its paragraph before and after it, read from that tab only at that moment. sentmine SHALL make the card at once: one word SHALL make its word card from its sentence; any other selection SHALL be the term (a word it starts or ends inside made whole), and the whole sentences it touches SHALL be the passage, also when it starts in one sentence and ends in the next. When the browser does not let the extension read the tab, the selection alone SHALL be sent. When sentmine is not running, the panel SHALL say so and how to start it.

#### Scenario: One word on a web page
- **WHEN** the reader double-clicks `discrete` on a web page and chooses "Make a card from this"
- **THEN** a card is made at once with `discrete` on the front and its whole sentence on the back

#### Scenario: A sentence on a web page
- **WHEN** the reader selects the end of one sentence and the start of the next and chooses the item
- **THEN** a card is made at once with the selection as its term and both whole sentences as its passage

#### Scenario: sentmine is not running
- **WHEN** the reader chooses the item and no sentmine answers
- **THEN** the panel says that sentmine is not running and to start it with `sentmine` in a terminal

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

### Requirement: Clips are kept apart from Read
Clips SHALL go to a reading session of their own. A new clip SHALL be added after the earlier ones, keeping their cards. The text and cards in Read SHALL NOT change because of a clip.

#### Scenario: Reading a PDF while clipping
- **WHEN** a PDF is open in Read with two cards, and the reader clips a sentence from a web page
- **THEN** Read still shows the PDF and its two cards

#### Scenario: Two clips
- **WHEN** the reader right-clicks one selection and then another
- **THEN** the panel shows both cards

### Requirement: Cards in the panel
The panel SHALL show sentmine's page with the cards only, not the text of the clips, since each right-click makes its card at once; a new card SHALL be scrolled into view. The cards SHALL be listed with Download and Send to Anki for them, open in Edit as in Read, and be remembered like any other card.

#### Scenario: A definition clip
- **WHEN** the reader selects "confounder" in "A confounder is a variable that influences both the treatment and the outcome." on a web page and chooses Make a card from this
- **THEN** a card is made with the term "confounder" and that sentence as its passage, and the panel shows it

### Requirement: The right-click needs no page access
The extension SHALL read a page only when the reader right-clicks in it or presses its button, and then only that tab (the permission for the active tab), taking the selection and the paragraph around it; it SHALL send it nowhere but sentmine on this computer.

#### Scenario: Permissions
- **WHEN** the reader loads the extension
- **THEN** it still does not ask to read all websites

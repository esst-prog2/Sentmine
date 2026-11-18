## ADDED Requirements

### Requirement: A card keeps its source
A card made from a PDF SHALL keep the file's name and the page it came from; a card made from a web page SHALL keep the page's title and its address, when the address starts with http or https. The source SHALL be shown on the card in the deck, written under the answer of the Anki card as text (a title is never treated as markup), and kept in the card memory. A card from a pasted text SHALL have no source line.

#### Scenario: A word on page 13
- **WHEN** the reader clicks a word on page 13 of primer.pdf
- **THEN** the card says From primer.pdf, p. 13, and its Anki card ends with that source

#### Scenario: An unsafe address
- **WHEN** a clip arrives with an address that does not start with http or https
- **THEN** the address is not kept

### Requirement: Sources in My cards
My cards SHALL show each remembered card's source, a web page's title linking to its address in a new tab, and SHALL list the sources most cards came from, at most five.

#### Scenario: Two books
- **WHEN** three remembered cards came from one PDF and one from a web page
- **THEN** My cards lists the PDF with 3 and the web page with 1

### Requirement: The memory is brought to layout 4 safely
Opening a card memory of an earlier layout SHALL add the source fields without changing its cards, and SHALL first keep a copy of a memory that has cards, beside it.

#### Scenario: A memory of layout 3
- **WHEN** a layout 3 memory with cards is opened
- **THEN** its cards are all there, it is at layout 4, and a copy at layout 3 is beside it

### Requirement: The two views stay in step
Read and the side panel SHALL each notice within a few seconds when the deck was changed in the other, and show it, without interrupting an edit, a waiting term, or a drag in progress.

#### Scenario: A card made in the side panel
- **WHEN** Read is open and the reader makes a card in the side panel
- **THEN** Read shows that card and the new count without the reader doing anything in Read

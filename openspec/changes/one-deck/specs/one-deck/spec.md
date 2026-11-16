## ADDED Requirements

### Requirement: One deck in both places
The cards made from the text in Read and from web pages SHALL be one deck: Read and the side panel SHALL show the same cards, and Download and Send to Anki SHALL take all of them. Each card SHALL show where it came from.

#### Scenario: A card from the PDF and one from the web
- **WHEN** the reader makes a card from the PDF in Read and one from a web page in the side panel
- **THEN** both places list the two cards, one from the PDF's name and one from a web page

### Requirement: The texts stay apart
A clip SHALL never change the text in Read. Each text SHALL mark only the words of its own cards. Reading a new text in Read SHALL remove only the cards made from the old text in Read, after asking, and SHALL keep the cards from web pages.

#### Scenario: A new text in Read
- **WHEN** the deck has a card from the text in Read and one from a web page, and the reader reads a new text
- **THEN** only the card from the web page is left

### Requirement: Pictures reach any card
A picture from a web page SHALL be able to go to any card in the deck, and a part of the PDF in Read SHALL be able to go to any card, including one from a web page.

#### Scenario: A web picture for a card from the PDF
- **WHEN** the reader presses Pictures go here on a card from the PDF and adds a picture from a web page
- **THEN** that card's back shows the picture

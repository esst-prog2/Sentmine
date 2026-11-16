## ADDED Requirements

### Requirement: A part of the page on a card
While a PDF is open, the reader SHALL be able to add to any card a picture of a box drawn on one of the PDF's pages. The picture SHALL be drawn from the PDF itself at a size that stays sharp, and SHALL be shown on the back of the card, under the answer; on a cloze card, in the field shown after the answer. The reader SHALL be able to remove a picture from a card. A box of less than a few pixels, or outside the page, SHALL be refused with a message.

#### Scenario: A formula on a word card
- **WHEN** the reader has a word card and drags a box around a formula on the page
- **THEN** the card's back shows the word and, under it, the picture of that formula

#### Scenario: Cancel
- **WHEN** the reader presses Add a picture and then Esc
- **THEN** no picture is added and the page works as before

### Requirement: Pictures from web pages
On a web page, the extension SHALL offer *Add this picture to the chosen card* on an image and *Add a part of this page to the chosen card* on the page. The chosen card SHALL be the newest card of the clips unless the reader chose another with *Pictures go here* in the side panel, and a new card SHALL become the chosen one. The first item SHALL put that image on the back of the chosen card; the second SHALL let the reader drag a box on the page and put that part, as seen on screen, on the same card. Esc SHALL cancel the box. When there is no card yet, the extension SHALL say to make one first. The app SHALL accept only PNG pictures of at most 5 MB this way.

#### Scenario: An image on Wikipedia
- **WHEN** the reader has made a word card in the side panel and right-clicks the article's photo and chooses Add this picture to the chosen card
- **THEN** that card's back shows the photo

#### Scenario: A formula on a web page
- **WHEN** the reader chooses Add a part of this page to the chosen card and drags a box around a formula
- **THEN** that card's back shows the formula as it looked on the page

#### Scenario: A card in the middle
- **WHEN** the reader has made three cards, presses Pictures go here on the second, and adds a picture from the page
- **THEN** the picture goes on the second card, not the newest

### Requirement: Picture only on the back
A card that has a picture SHALL have a switch to show only its pictures on the back, leaving out the text there. Switched off, the back SHALL be the text with the pictures under it.

#### Scenario: A word and its picture
- **WHEN** the reader switches a word card with a picture to Picture only on the back
- **THEN** the card in Anki has the sentence with the word on the front and only the picture on the back

### Requirement: Pictures go to Anki
A downloaded deck SHALL contain the pictures of its cards as media files, and Send to Anki SHALL store them in Anki's media before adding the notes, so the notes show them. A picture's file name SHALL come from its content, so the same picture is stored once.

#### Scenario: Download
- **WHEN** the reader downloads a deck with a card that has a picture
- **THEN** the deck file contains that picture and the card's back refers to it

#### Scenario: Send to Anki
- **WHEN** the reader sends that card to Anki
- **THEN** the picture is stored in Anki's media before the note is added

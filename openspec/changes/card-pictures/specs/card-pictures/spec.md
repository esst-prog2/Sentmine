## ADDED Requirements

### Requirement: A part of the page on a card
While a PDF is open, the reader SHALL be able to add to any card a picture of a box drawn on one of the PDF's pages. The picture SHALL be drawn from the PDF itself at a size that stays sharp, and SHALL be shown on the back of the card, under the answer; on a cloze card, in the field shown after the answer. The reader SHALL be able to remove a picture from a card. A box of less than a few pixels, or outside the page, SHALL be refused with a message.

#### Scenario: A formula on a word card
- **WHEN** the reader has a word card and drags a box around a formula on the page
- **THEN** the card's back shows the word and, under it, the picture of that formula

#### Scenario: Cancel
- **WHEN** the reader presses Add a picture and then Esc
- **THEN** no picture is added and the page works as before

### Requirement: Pictures go to Anki
A downloaded deck SHALL contain the pictures of its cards as media files, and Send to Anki SHALL store them in Anki's media before adding the notes, so the notes show them. A picture's file name SHALL come from its content, so the same picture is stored once.

#### Scenario: Download
- **WHEN** the reader downloads a deck with a card that has a picture
- **THEN** the deck file contains that picture and the card's back refers to it

#### Scenario: Send to Anki
- **WHEN** the reader sends that card to Anki
- **THEN** the picture is stored in Anki's media before the note is added

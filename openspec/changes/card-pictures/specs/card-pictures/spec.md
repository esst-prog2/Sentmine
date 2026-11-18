## ADDED Requirements

### Requirement: Each side of a card is a small document
Pressing Edit on a card SHALL open its front and its back as editable documents of text and pictures, each picture at the place the reader put it, on either side. The reader SHALL be able to type above and below a picture, and remove a picture by selecting it (a click) and pressing Delete, or by Backspace or Delete beside it. Save SHALL keep the arrangement, and a picture removed from both sides SHALL be removed from the card. A cloze card SHALL hide the front's text and show the front's pictures after the answer; the memory SHALL keep each side's text with [picture] where a picture was; a suggested meaning SHALL be asked with the sentence's text only. Opening Edit SHALL make that card the one pictures from a web page go to; there SHALL be no separate button for choosing it.

#### Scenario: A line under a picture
- **WHEN** the reader edits a card, pastes a picture after the first line, types a line under it, and saves
- **THEN** the card's back shows the first line, the picture, then the new line, in that order

#### Scenario: A graph on the front
- **WHEN** the reader edits a card, puts the cursor in the front, pastes a graph, and saves
- **THEN** the card's front shows its text and the graph

#### Scenario: Removing a picture
- **WHEN** the reader clicks a picture in the editor, presses Delete, and saves
- **THEN** the picture is no longer on the card

### Requirement: A part of the page on a card
While a PDF is open in Read and a card is being edited, a box the reader drags on one of the PDF's pages SHALL go into the card as a picture, at its cursor. The picture SHALL be drawn from the PDF itself at a size that stays sharp. On a cloze card, it SHALL be in the field shown after the answer. A box of less than a few pixels, or outside the page, SHALL be refused with a message.

#### Scenario: A formula on a word card
- **WHEN** the reader edits a word card and drags a box around a formula on the page
- **THEN** the editor shows the picture of that formula, and what was typed is kept

#### Scenario: Cancel
- **WHEN** the reader starts a box on the page and presses Esc before letting go
- **THEN** no picture is added and the page works as before

### Requirement: Pictures from web pages
On a web page, the extension SHALL offer *Add this picture to the card you last made or edited* on an image, which SHALL put that image at the end of that card's back. A new card, or a card the reader opens with Edit, SHALL become that card. While the card is open in the editor, the picture SHALL appear in the editor without losing what is typed. When there is no card yet, the extension SHALL say to make one first. The app SHALL accept only PNG pictures of at most 5 MB this way.

#### Scenario: An image on Wikipedia
- **WHEN** the reader has made a word card and right-clicks the article's photo and chooses Add this picture to the card you last made or edited
- **THEN** that card's back shows the photo

#### Scenario: A card in the middle
- **WHEN** the reader has made two cards, presses Edit on the first, types a word, and adds a picture from the page
- **THEN** the picture goes on the first card, not the newest, and the editor shows it next to the typed word

### Requirement: Pasting a picture
Pasting an image (a copied picture or a screenshot) in Read or in the side panel SHALL put it in the card being edited, where the cursor is on either side (at the end of the back when the cursor is in neither), or else at the end of the card last made or edited. It SHALL be stored as a PNG no wider than 1600 pixels. What is typed in the editor SHALL be kept. Pasted text SHALL be pasted as usual. With no card, the page SHALL say to make one first.

#### Scenario: A screenshot while editing
- **WHEN** the reader is editing a card, has typed two lines, puts the cursor after the first, and pastes a screenshot
- **THEN** the picture is between the two lines and the typed text is still in the editor

### Requirement: Pictures go to Anki
A downloaded deck SHALL contain the pictures of its cards as media files, at their places in the card, and Send to Anki SHALL store them in Anki's media before adding the notes, so the notes show them. A picture's file name SHALL come from its content, so the same picture is stored once.

#### Scenario: Download
- **WHEN** the reader downloads a deck with a card that has a picture
- **THEN** the deck file contains that picture and the card's back refers to it

#### Scenario: Send to Anki
- **WHEN** the reader sends that card to Anki
- **THEN** the picture is stored in Anki's media before the note is added

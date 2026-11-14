# clip-panel Specification

## Purpose
Make cards from text selected on a web page, with one right-click, in a side panel beside the page, kept apart from the text in Read.

## Requirements

### Requirement: Right-click on selected text
The extension SHALL add two items to the menu of selected text on a web page: "Word card from this sentence" and "Definition card from this". Choosing one SHALL open the side panel and send the selected text to sentmine as a clip of that kind. When sentmine is not running, the panel SHALL say so and how to start it.

#### Scenario: A sentence on a web page
- **WHEN** the reader selects a sentence on a web page and chooses "Word card from this sentence"
- **THEN** the side panel shows that sentence with its words clickable

#### Scenario: sentmine is not running
- **WHEN** the reader chooses either item and no sentmine answers
- **THEN** the panel says that sentmine is not running and to start it with `sentmine` in a terminal

### Requirement: Clips are kept apart from Read
Clips SHALL go to a reading session of their own. A new clip SHALL be added after the earlier ones, keeping their cards. The text and cards in Read SHALL NOT change because of a clip.

#### Scenario: Reading a PDF while clipping
- **WHEN** a PDF is open in Read with two cards, and the reader clips a sentence from a web page
- **THEN** Read still shows the PDF and its two cards

#### Scenario: Two clips
- **WHEN** the reader makes a card from one clip and then clips another sentence
- **THEN** the panel shows both clips and keeps the first card

### Requirement: Cards in the panel
The panel SHALL show sentmine's page for the clips: a click on a word makes a word card from its sentence, as in Read. In a definition clip, a drag over the term SHALL make a definition card whose definition is the whole clip. The cards SHALL be listed in the panel, with Download and Send to Anki for them, and remembered like any other card.

#### Scenario: A definition clip
- **WHEN** the reader clips "A confounder is a variable that influences both the treatment and the outcome." as a definition and drags over "confounder"
- **THEN** a definition card is made with the term "confounder" and that sentence as its definition

### Requirement: The right-click needs no page access
The extension SHALL make clips from the selected text the browser hands it, without reading the page, and SHALL send it nowhere but sentmine on this computer.

#### Scenario: Permissions
- **WHEN** the reader loads the extension
- **THEN** it still does not ask to read all websites

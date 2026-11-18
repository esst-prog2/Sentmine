## ADDED Requirements

### Requirement: One shape for every card
Every card SHALL have the term on the front and the passage on the back, with every whole-word place of the term in the passage in bold. A card made from one word SHALL have the word, lower-cased and followed by its base form in brackets when that differs, on the front, and the sentence the word is in on the back, with the word in bold as written. The card SHALL keep whether it was made from one word, so that it is found again by its base form, as before.

#### Scenario: A word and a term look the same
- **WHEN** the reader makes a card from the word `skew` in `Outliers can skew the mean considerably.` and a card from the term `confounder` with the passage `A confounder is a variable.`
- **THEN** the first card shows `skew` on the front and `Outliers can **skew** the mean considerably.` on the back, and the second shows `confounder` and `A **confounder** is a variable.`

### Requirement: A rough selection is taken as whole sentences
A passage selected on a web page, or dragged in Read for a definition, SHALL be taken as the whole sentences it touches, with the sentences found in the text around it. A passage that is not found in the text SHALL be kept as it is.

#### Scenario: A selection that starts inside a word
- **WHEN** the reader selects `ers. Outliers can` in `The median resists outliers. Outliers can skew the mean. Next.`
- **THEN** the passage is `The median resists outliers. Outliers can skew the mean.`

### Requirement: Cards remembered in the earlier shape
A word card remembered before this change, with its sentence on the front and the word on the back, SHALL be shown as it was made, and SHALL NOT be offered as a cloze card.

#### Scenario: An old card in My cards
- **WHEN** the memory holds a word card with the front `Its owner sighed.` and the back `sighed (sigh)`
- **THEN** My cards shows `Its owner **sighed**.` on its front and `sighed (sigh)` on its back

### Requirement: Suggest meaning under the passage
*Suggest meaning* on a card made from one word SHALL ask with the word and its sentence and put the meaning under the passage, replacing the meaning it put there before when that is still there. The same request SHALL ask for the few words of the sentence that show the meaning; the card SHALL underline them on its back only when they are a part of the sentence, of at most eight words and not the whole sentence, and SHALL keep the meaning without an underline otherwise. The underline SHALL NOT be part of the text the reader edits, and an edit that changes those words SHALL drop it.

#### Scenario: Pressing it twice
- **WHEN** the reader presses Suggest meaning on the card for `skew`, then again
- **THEN** the back is the sentence and, under it, only the second meaning

#### Scenario: The words that show the meaning
- **WHEN** the model answers the meaning of `simultaneously` with the key `flipped simultaneously to determine`
- **THEN** the back shows those words of the sentence underlined, with `simultaneously` still in bold

#### Scenario: Words that are not in the sentence
- **WHEN** the model names words that are not in the sentence, or the whole sentence
- **THEN** the meaning is put on the card and nothing is underlined

### Requirement: Edit puts things in at the cursor
While a card is open in Edit, the reader SHALL be able to put into it, at the place of its cursor in the Term or the Passage (the end of the Passage when there is none): the whole sentence of a word clicked in the text of the same view; the sentences of a drag over the text; on a PDF in Read, a picture of a box dragged on a page (a click instead of a drag puts in the sentence clicked); a pasted picture; and, from a web page, the whole sentences of text right-clicked with *Make a card from this* and an image right-clicked with *Add this picture*. Nothing put in this way SHALL make a card. Put-in text SHALL keep a space from the words around it, and the cursor SHALL go on after it. While the cursor is away from the card, a mark SHALL show where the next thing goes. Undo (also Ctrl+Z) SHALL take back the last thing put in, deleted or typed (a run of typing counts as one step), one step at a time, and Redo (also Ctrl+Y or Ctrl+Shift+Z) SHALL put it back; each SHALL be greyed out when there is nothing to take back or put back. A right-click on a web page SHALL NOT load the side panel's page again, so a card open in Edit there stays open. Save SHALL end the edit; Cancel SHALL put the card back as it was, with no picture added. A page closed while editing SHALL count as closed after three minutes.

#### Scenario: A sentence further on
- **WHEN** the reader edits the card for `random`, puts the cursor at the start of its passage and clicks a word of the sentence before it
- **THEN** that sentence is at the start of the passage, followed by the card's own sentence, and no new card is made

#### Scenario: A box on the PDF page
- **WHEN** the reader then drags a box around a formula on the page
- **THEN** its picture is in the passage just after the sentence put in

#### Scenario: Text from a web page
- **WHEN** a card is open in Edit in the side panel and the reader right-clicks a sentence on the web page and chooses *Make a card from this*
- **THEN** that sentence is put in at the card's cursor, and no clip or card is made

#### Scenario: Undo, step by step
- **WHEN** the reader puts in a sentence, types a word, and draws a box on the PDF page, then presses Undo three times
- **THEN** the picture goes first, then the word, then the sentence; Redo puts them back in that order

#### Scenario: Cancel
- **WHEN** the reader puts in a picture and a sentence, then presses Cancel
- **THEN** the card is as it was before Edit

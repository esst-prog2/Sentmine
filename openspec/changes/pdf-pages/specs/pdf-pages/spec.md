## ADDED Requirements

### Requirement: A PDF is shown as its pages
When the reader opens a PDF, the reading page SHALL show each of its pages as it looks in the PDF, in order, instead of the extracted text. A pasted text or a text file SHALL be shown as text, as before. Pages SHALL be drawn when they come near the screen, not all when the PDF is opened.

#### Scenario: Opening a PDF
- **WHEN** the reader opens a PDF of two pages
- **THEN** the reading panel shows two pages, each as a picture of that page

#### Scenario: Pasting after a PDF
- **WHEN** a PDF is shown and the reader pastes a text
- **THEN** the pasted text is shown as text and the pages are gone

### Requirement: The words of the text are found on the pages
Each word of the text read from the PDF SHALL be found on the page where it is printed, ignoring upper and lower case, running heads and page numbers that are not in the text, numbers between words, and words broken at a line end. A word broken across two lines SHALL be found on both. The same words printed twice SHALL each be found where they are.

#### Scenario: A broken word
- **WHEN** a page has `consid-` at the end of one line and `erably` at the start of the next
- **THEN** the word `considerably` of the text is found on both lines

#### Scenario: Words around numbers
- **WHEN** a page has `Male 112 High school 231 College 595.`
- **THEN** every word of that sentence is found on the page

#### Scenario: Repeated text
- **WHEN** the same sentence is on page 1 and on page 2
- **THEN** its first copy in the text is found on page 1 and its second on page 2

### Requirement: Picking on the pages
A click on a word printed on a page and a drag over printed text SHALL do what they do on a pasted text, using the word's sentence from the text: a click makes or removes a word card, and drags choose a term and its definition. A press that moves 5 pixels or more SHALL be a drag and a press that moves less SHALL be a click. A drag SHALL run from the word nearest the press to the word nearest the pointer, so it may start in the space between words, and the words it covers SHALL be marked while it goes on. Dragging near the top or bottom of the window SHALL scroll it. A word with a card SHALL be marked on the page. A passage dragged over the pages SHALL be the text from the first word selected to the last, with its spaces, paragraph breaks and the punctuation right after the last word.

#### Scenario: A click on a page
- **WHEN** the reader clicks `Suppose` printed in `Suppose we have three cards.`
- **THEN** a word card is made with the front `Suppose we have three cards.` and `Suppose` is marked on the page

#### Scenario: A definition dragged over the pages
- **WHEN** the reader drags over `random` and then from `Suppose` to `also black` at the end of the next sentences
- **THEN** a definition card is made for `random` whose passage starts `Suppose we have three cards.` and ends `is also black?`

#### Scenario: A click that wobbles
- **WHEN** the reader presses on `Suppose`, moves 2 pixels and lets go
- **THEN** a word card is made for `Suppose`, as for a click

#### Scenario: A drag from the margin
- **WHEN** the reader presses in the margin left of `Suppose` and drags to the end of `cards`
- **THEN** the five words are marked while dragging, and `Suppose we have three cards.` becomes the term

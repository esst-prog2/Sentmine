## MODIFIED Requirements

### Requirement: Word cards
The reader SHALL be able to click any word of the text. A click on a word that has no card SHALL make a word card whose front is the sentence the word is in and whose back is the word, lower-cased, followed by its base form in brackets when the base form differs from it (`sighed (sigh)`). A click on the very word that made a card SHALL remove that card. Words are found by the rules of the `passage-analysis` capability; a token containing a digit is not a word and cannot be clicked.

#### Scenario: Picking a word
- **WHEN** the text contains `Outliers can skew it considerably.` and the reader clicks `skew`
- **THEN** a card is made with the front `Outliers can skew it considerably.` and the back `skew`

#### Scenario: A word whose base form differs
- **WHEN** the reader clicks `sighed`
- **THEN** the back of its card is `sighed (sigh)`

#### Scenario: Unpicking a word
- **WHEN** the reader clicks the same `skew` again
- **THEN** its card is removed and the number of cards goes down by one

### Requirement: Definition cards
The reader SHALL be able to drag over a term of one or more words and then drag over the passage that defines it. The app SHALL make a definition card whose front is the term and whose back is the marked passage. The passage MAY be one sentence, several sentences, or several paragraphs. A break between paragraphs inside the passage SHALL be kept; other runs of spaces SHALL become one space. An empty term or an empty passage SHALL be refused with a message.

#### Scenario: A two-sentence definition
- **WHEN** the reader drags over the term `standard deviation` and then over `The standard deviation measures how spread out a set of values is. It is the square root of the variance.`
- **THEN** a card is made with the front `standard deviation` and exactly that passage as the back

#### Scenario: A definition across two paragraphs
- **WHEN** the marked passage runs from one paragraph into the next
- **THEN** the back of the card keeps the break between the two paragraphs

#### Scenario: Nothing marked
- **WHEN** the term or the passage is empty
- **THEN** no card is made and a message says what is missing

## ADDED Requirements

### Requirement: A click and a drag are told apart
The reading page SHALL NOT have a switch between word cards and definition cards. A click on a word, with no text selected, SHALL act on word cards. A drag that selects text in the reading panel SHALL choose a term when no term is waiting, and SHALL mark the definition of the waiting term otherwise. While a term is waiting, the page SHALL name it and offer to cancel it; Esc SHALL cancel it, and a click on a word SHALL cancel it before acting on word cards. A double-click or triple-click SHALL act as a single click and SHALL NOT choose a term.

#### Scenario: A click makes a word card
- **WHEN** no term is waiting and the reader clicks `skew`
- **THEN** a word card is made for `skew`, and no term is chosen

#### Scenario: Two drags make a definition card
- **WHEN** the reader drags over `standard deviation` and then over a passage
- **THEN** after the first drag the page names `standard deviation` as the waiting term and no card is made; after the second a definition card is made and no term is waiting

#### Scenario: A drag inside one word
- **WHEN** the reader drags across the single word `variance`
- **THEN** `variance` becomes the waiting term and no word card is made

#### Scenario: Cancelling a term
- **WHEN** a term is waiting and the reader presses Esc or the Cancel button
- **THEN** no term is waiting and no card is made

#### Scenario: A click while a term is waiting
- **WHEN** a term is waiting and the reader clicks `skew`
- **THEN** the term is no longer waiting and a word card is made for `skew`

#### Scenario: A double-click
- **WHEN** no term is waiting and the reader double-clicks `skew`
- **THEN** one word card is made for `skew` and no term is chosen

## Purpose

Lets a reader paste a text, choose while reading what becomes a flashcard, check every card, and download the cards as an Anki deck.

## ADDED Requirements

### Requirement: The app runs on the reader's own computer
The reading app SHALL be a web page served only on the reader's own computer (address `127.0.0.1`). It SHALL NOT send the text or the cards to any other machine, and SHALL NOT need an account or an external service. It SHALL keep one text and its cards in memory and SHALL write nothing to disk; the only file is the deck the browser downloads.

#### Scenario: Offline
- **WHEN** the machine has no network connection
- **THEN** the page opens and every feature works

### Requirement: Pasting and tidying a text
The app SHALL accept a pasted plain text of any length. It SHALL tidy the text before showing it: paragraphs are the parts separated by one or more blank lines; a single line break inside a paragraph becomes one space; runs of spaces and tabs become one space; empty paragraphs are dropped. Loading a text SHALL discard the text and cards loaded before it. An empty text, or one with only spaces and line breaks, SHALL be refused with a message and SHALL leave the current text and cards as they are.

#### Scenario: Wrapped lines are joined
- **WHEN** the pasted text is `Outliers can skew it` followed by a line break and `considerably.`
- **THEN** the page shows the single sentence `Outliers can skew it considerably.`

#### Scenario: Paragraphs are kept
- **WHEN** the pasted text has two parts separated by a blank line
- **THEN** the page shows two paragraphs

#### Scenario: Empty paste
- **WHEN** the pasted text is empty
- **THEN** the app refuses it with a message and the text and cards on the page do not change

### Requirement: Word cards
In Word mode the reader SHALL be able to click any word of the text. A click on a word that has no card SHALL make a word card whose front is the sentence the word is in and whose back is the word, lower-cased. A click on the very word that made a card SHALL remove that card. Words are found by the rules of the `passage-analysis` capability; a token containing a digit is not a word and cannot be clicked.

#### Scenario: Picking a word
- **WHEN** the text contains `Outliers can skew it considerably.` and the reader clicks `skew`
- **THEN** a card is made with the front `Outliers can skew it considerably.` and the back `skew`

#### Scenario: Unpicking a word
- **WHEN** the reader clicks the same `skew` again
- **THEN** its card is removed and the number of cards goes down by one

### Requirement: Definition cards
In Definition mode the reader SHALL be able to select a term of one or more words and then mark the passage that defines it. The app SHALL make a definition card whose front is the term and whose back is the marked passage. The passage MAY be one sentence, several sentences, or several paragraphs. A break between paragraphs inside the passage SHALL be kept; other runs of spaces SHALL become one space. An empty term or an empty passage SHALL be refused with a message.

#### Scenario: A two-sentence definition
- **WHEN** the reader selects the term `standard deviation` and marks `The standard deviation measures how spread out a set of values is. It is the square root of the variance.`
- **THEN** a card is made with the front `standard deviation` and exactly that passage as the back

#### Scenario: A definition across two paragraphs
- **WHEN** the marked passage runs from one paragraph into the next
- **THEN** the back of the card keeps the break between the two paragraphs

#### Scenario: Nothing marked
- **WHEN** the term or the passage is empty
- **THEN** no card is made and a message says what is missing

### Requirement: One card per word or term
The app SHALL NOT make a second card for a word or term that already has one, and SHALL tell the reader that it already has a card. Two words are the same when their stems match (`sigh` and `sighed`). Two terms are the same when they match ignoring upper and lower case and spacing. A word card and a definition card for the same text MAY both exist.

#### Scenario: Second occurrence of a word
- **WHEN** `stubborn` has a card and the reader clicks another `stubborn` elsewhere in the text
- **THEN** no card is made, the number of cards stays the same, and a message says the word already has a card

#### Scenario: Another form of a word
- **WHEN** `sighed` has a card and the reader clicks `sigh`
- **THEN** no card is made

#### Scenario: Same term again
- **WHEN** `standard deviation` has a card and the reader makes a definition card for `Standard  Deviation`
- **THEN** no card is made

### Requirement: Preview, edit and delete
The page SHALL show every card, front and back, in the order the cards were made. The reader SHALL be able to change the front and the back of any card and to delete any card. An edited word card SHALL still show its word in bold wherever the word occurs in the edited front.

#### Scenario: Editing a card
- **WHEN** the reader changes the back of a card
- **THEN** the preview shows the changed back

#### Scenario: Deleting a card
- **WHEN** the reader deletes a card
- **THEN** it leaves the preview, the number of cards goes down by one, and its word can be picked again

### Requirement: Card count
The page SHALL show the number of cards at all times, with singular and plural agreeing with the number.

#### Scenario: Two cards
- **WHEN** two cards have been made
- **THEN** the header says `2 cards`

### Requirement: Download
Download SHALL give the reader an `.apkg` deck holding the cards exactly as the preview shows them, in the same order. The file name SHALL be the deck name the reader gave, `new` by default, with `.apkg`. With no cards, Download SHALL give no file and SHALL say why.

#### Scenario: Edited text is what is downloaded
- **WHEN** a card was edited in the preview and the deck is downloaded
- **THEN** the deck holds the edited text, not the original

#### Scenario: No cards
- **WHEN** Download is pressed with no cards
- **THEN** no file is given and a message says there are no cards yet

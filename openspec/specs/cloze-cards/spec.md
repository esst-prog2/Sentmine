# cloze-cards Specification

## Purpose
TBD - created by archiving change cloze-cards. Update Purpose after archive.

## Requirements

### Requirement: A definition card can be a cloze card
Each definition card SHALL be either a cloze card or a term → passage card, and the reader SHALL be able to switch it in the preview. A new definition card SHALL start as a cloze card when its term appears in its passage as a whole word, ignoring case, and as a term → passage card otherwise. A cloze card SHALL hide every place the term appears in the passage. Switching to cloze SHALL be refused with a message when the term is not in the passage. An edit that removes the term from the passage SHALL make the card a term → passage card.

#### Scenario: The term is in the passage
- **WHEN** the reader marks the term `standard deviation` and the passage `The standard deviation measures how spread out a set of values is.`
- **THEN** the card is a cloze card, and its front is `The [...] measures how spread out a set of values is.`

#### Scenario: A word that only contains the term
- **WHEN** the term is `variance` and the passage is `The covariance of two variables.`
- **THEN** the card starts as a term → passage card

#### Scenario: Switching
- **WHEN** the reader switches a cloze card to term → passage
- **THEN** its front is the term and its back is the passage, as before this change

### Requirement: Cloze cards in Anki
Download and Send to Anki SHALL write a cloze card as a note of the note type `sentmine: cloze`, which is of Anki's cloze kind, with the passage in its first field and every place of the term marked as `{{c1::...}}`. The note type SHALL be made in Anki if it is missing. Word cards and term → passage cards SHALL be written as before. Send to Anki SHALL count a cloze note as already there only if a sentmine note in the deck has exactly the same first field.

#### Scenario: Downloading a cloze card
- **WHEN** a deck with one cloze card for `standard deviation` is downloaded
- **THEN** its note's first field is `The {{c1::standard deviation}} measures how spread out a set of values is.`

#### Scenario: Sending both kinds
- **WHEN** a word card and a cloze card are sent to a deck in an Anki that has neither sentmine note type
- **THEN** both note types are made and both notes are added

### Requirement: The memory is not changed by cloze
A cloze card SHALL be remembered as a definition card with its term and passage, so earlier cards are found and My cards shows it as before.

#### Scenario: Remembered as a definition
- **WHEN** a cloze card for `standard deviation` is downloaded
- **THEN** My cards lists a definition card with the front `standard deviation` and the passage as its back

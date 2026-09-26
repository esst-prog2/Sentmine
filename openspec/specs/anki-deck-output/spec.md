# anki-deck-output Specification

## Purpose

Turns the new words into Anki flashcards that teach each word inside the sentence where it was met, and packages them as a deck Anki can import.

## Requirements

### Requirement: One card per new word
The tool SHALL write one card for each new word, in the order the words first appear in the passage. The back of the card SHALL be the word as it appeared in the sentence, lower-cased. The front SHALL be the sentence in which the word first appeared.

#### Scenario: Card for a new word
- **WHEN** `stubborn` is a new word first seen in `The stubborn old dog refused to move.`
- **THEN** the card front is that sentence with `stubborn` in bold
- **AND** the card back is `stubborn`

#### Scenario: Inflected form on the back
- **WHEN** `sighed` is a new word
- **THEN** the card back is `sighed`, not `sigh`

#### Scenario: Card order
- **WHEN** the new words first appear in the order `stubborn`, `refused`, `sighed`, `resilient`, `equally`
- **THEN** the deck holds the cards in that order

### Requirement: Card front shows the sentence unchanged apart from bold
The card front SHALL be the stored sentence with `<`, `>` and `&` escaped so they display as typed. Every whole-word occurrence of the card word in that sentence SHALL be wrapped in bold, matched as written and ignoring case, and the original letter case SHALL be kept. Nothing else in the sentence SHALL change.

#### Scenario: Word appears twice in the sentence
- **WHEN** the sentence is `The stubborn dog was stubborn.` and the card word is `stubborn`
- **THEN** both occurrences are bold

#### Scenario: Original case kept
- **WHEN** the card word is `stubborn` and the sentence starts `Stubborn dogs sulk.`
- **THEN** `Stubborn` is bold and keeps its capital letter, and the card back is `stubborn`

#### Scenario: Special characters
- **WHEN** the sentence is `AT&T said x < y.`
- **THEN** the front displays `AT&T said x < y.` as typed, without breaking the card

#### Scenario: Part of a longer word is not bolded
- **WHEN** the card word is `dog` and the sentence contains `dogged`
- **THEN** `dogged` is not bold

### Requirement: Valid Anki deck
The tool SHALL write a deck file that Anki imports without error. The number of cards imported SHALL equal the number of cards the tool reports writing.

#### Scenario: Import into Anki
- **WHEN** the deck written for the demo passage is imported into Anki
- **THEN** the import succeeds and Anki shows 5 new cards

#### Scenario: Card count matches
- **WHEN** the tool reports `Wrote 5 new cards`
- **THEN** the deck contains exactly 5 cards

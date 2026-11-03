# send-to-anki Specification

## Purpose
TBD - created by archiving change send-to-anki. Update Purpose after archive.

## Requirements

### Requirement: Sending the cards to Anki
The reading page SHALL have a Send to Anki button. It SHALL add the cards, exactly as the preview shows them and in the same order, to the open Anki on the reader's computer through AnkiConnect, in the deck named in the deck-name box, cleaned by the same rule as the deck file name. The deck SHALL be made if it does not exist. The note type SHALL be the one the `.apkg` deck uses, made in Anki if it is missing. Requests SHALL go to `127.0.0.1` only. With no cards, nothing SHALL be sent and a message SHALL say why.

#### Scenario: Sending three cards
- **WHEN** the preview holds three cards, the deck name is `stats`, and Anki is open with AnkiConnect
- **THEN** Anki's deck `stats` holds three new notes with the preview's fronts and backs, and the message says 3 cards were added

#### Scenario: The note type is missing
- **WHEN** Anki has no sentmine note type yet
- **THEN** it is made, with the fields Front and Back, before the notes are added

### Requirement: Cards already in the deck
A card whose front is already in that deck with the sentmine note type SHALL NOT be added again. The other cards SHALL still be added, and the message SHALL say how many were added and how many were already there.

#### Scenario: One card already there
- **WHEN** three cards are sent and the deck already has the first one
- **THEN** two notes are added and the message says 2 were added and 1 was already there

### Requirement: Sent cards are remembered
After a send that reached Anki, every card sent, including those already there, SHALL be added to the card memory by the same rule as for Download.

#### Scenario: Remembered after sending
- **WHEN** two cards are sent and Anki accepts them
- **THEN** both appear in My cards

### Requirement: Anki cannot be reached
If Anki is not open, AnkiConnect is not installed or is too old, or Anki refuses the request, nothing SHALL be remembered, the preview SHALL stay as it was, and a message SHALL say in plain words what to do. Download SHALL still work.

#### Scenario: Anki is closed
- **WHEN** the reader presses Send to Anki and nothing answers on AnkiConnect's address
- **THEN** the message says Anki is not open or AnkiConnect is not installed, and the cards stay in the preview

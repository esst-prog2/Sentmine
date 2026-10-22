# card-history Specification

## Purpose
TBD - created by archiving change remember-cards. Update Purpose after archive.

## Requirements

### Requirement: Where the history is kept
The reading app SHALL keep the history of the reader's cards in one file in the reader's own user folder: on Windows `%APPDATA%\sentmine\history.jsonl`, elsewhere `~/.local/share/sentmine/history.jsonl`. The environment variable `SENTMINE_HISTORY` SHALL, when set, name a different file. The file SHALL NOT be inside the program or the repository. A missing file SHALL mean an empty history; the file and its folder SHALL be created when the first card is added.

#### Scenario: First use
- **WHEN** the history file does not exist and a deck with two cards is downloaded
- **THEN** the file is created and holds two entries

### Requirement: What an entry holds
Each entry SHALL record: whether the card was a word card or a definition card; its key (the base form of the word, or the term in lower case with single spaces); the front and back as they were downloaded; for a word card, the word as clicked; and the date of the download (`YYYY-MM-DD`).

#### Scenario: A word card
- **WHEN** a card for `sighed` from `Its owner sighed.` is downloaded on 17 October 2026
- **THEN** its entry has the kind `word`, the key `sigh`, the front `Its owner sighed.`, the back `sighed (sigh)`, the word `sighed` and the date `2026-10-17`

### Requirement: Cards are added when they are downloaded
A card SHALL be added to the history when a deck containing it is downloaded, and not before. A card that is deleted in the preview, or a session closed without downloading, SHALL leave no entry. Downloading the same card again, with the same kind, key, front and back, SHALL NOT add a second entry.

#### Scenario: Deleted before download
- **WHEN** the reader makes a card, deletes it, and downloads the deck with the other cards
- **THEN** the deleted card is not in the history

#### Scenario: The same deck downloaded twice
- **WHEN** the reader downloads the same deck twice
- **THEN** each card is in the history once

### Requirement: Finding an earlier card
The app SHALL find an earlier card by kind and key. When several entries match, it SHALL use the most recent one.

#### Scenario: A different form of an earlier word
- **WHEN** the history holds a word card for `run` and the reader picks `ran`
- **THEN** that card is found

### Requirement: A history that cannot be read
If the history file exists but cannot be read, or a line of it is not a valid entry, the app SHALL tell the reader that the history could not be read and SHALL go on working without it: no earlier card is found, and downloads still work. It SHALL NOT overwrite or delete the file. If adding to the history fails during a download, the deck SHALL still be downloaded and the reader SHALL be told that the cards were not remembered.

#### Scenario: A damaged file
- **WHEN** the history file contains a line that is not a valid entry
- **THEN** the page says the history could not be read, picking words still makes cards, and the file is unchanged

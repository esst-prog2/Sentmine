## MODIFIED Requirements

### Requirement: Where the history is kept
The reading app SHALL keep the memory of the reader's cards in one SQLite database file, `cards.db`, in the reader's own user folder: on Windows `%APPDATA%\sentmine\`, elsewhere `~/.local/share/sentmine/`. The environment variable `SENTMINE_DATABASE` SHALL, when set, name a different database file. The file SHALL NOT be inside the program or the repository. The database and its folder SHALL be created when the app first opens it.

#### Scenario: First use
- **WHEN** no database exists and a deck with two cards is downloaded
- **THEN** the database is created and holds two cards

### Requirement: What an entry holds
Each remembered card SHALL have a number of its own and SHALL record: whether it is a word card or a definition card; its key (the base form of the word, or the term in lower case with single spaces); the front and back as they were downloaded; for a word card, the word as clicked; and the date of the download (`YYYY-MM-DD`). Two cards with the same kind, key, front and back SHALL be stored once.

#### Scenario: A word card
- **WHEN** a card for `sighed` from `Its owner sighed.` is downloaded on 17 October 2026
- **THEN** the memory holds a word card with the key `sigh`, the front `Its owner sighed.`, the back `sighed (sigh)`, the word `sighed` and the date `2026-10-17`

### Requirement: A history that cannot be read
If the database cannot be opened, is not a database, or was made by a newer version of the app, the app SHALL tell the reader why and SHALL go on working without a memory: no earlier card is found, downloads still work, and the reader is told that the cards were not remembered. The app SHALL NOT overwrite, repair or delete the file.

#### Scenario: A damaged database
- **WHEN** the database file is not a SQLite database
- **THEN** the page says the memory could not be opened, picking words still makes cards, downloads still work, and the file is unchanged

## ADDED Requirements

### Requirement: Schema versions
The database SHALL record the version of its layout. When the app opens a database with an older layout, it SHALL bring it up to date, one step at a time, each step complete or not at all. A database with a newer layout than the app knows SHALL be treated as one that cannot be read.

#### Scenario: A newer database
- **WHEN** the database records a layout version higher than the app knows
- **THEN** the app works without a memory and says the database was made by a newer version

### Requirement: Moving the old history file into the database
When the app opens a database that has not yet taken in the old history file, and the file `history.jsonl` exists in the same user folder, it SHALL copy every card of that file into the database, keeping their dates, in one step. It SHALL do this once, and SHALL leave the old file unchanged. If the old file cannot be read, nothing SHALL be copied, the reader SHALL be told which file and why, and the app SHALL try again at the next start.

#### Scenario: Cards from the old file
- **WHEN** `history.jsonl` holds three cards and the new version starts for the first time
- **THEN** the database holds the same three cards with their dates, and the old file is unchanged

#### Scenario: Only once
- **WHEN** the app starts a second time
- **THEN** the cards are not copied again

#### Scenario: A damaged old file
- **WHEN** a line of `history.jsonl` is not a card
- **THEN** no card is copied, the reader is told which file could not be read, and the file is unchanged

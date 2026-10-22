# my-cards Specification

## Purpose
TBD - created by archiving change memory-database. Update Purpose after archive.

## Requirements

### Requirement: The My cards page
The app SHALL have a page, My cards, reachable by a link from the reading page and back. It SHALL list the remembered cards newest first, each with its kind, front, back and date, showing at most 200 and saying how many there are in all.

#### Scenario: Three cards
- **WHEN** the memory holds cards from 9, 17 and 22 October
- **THEN** the page lists them in the order 22, 17, 9 October and says there are 3 cards

### Requirement: Search
The page SHALL have a search box. Typing in it SHALL list only the cards whose word, key, front or back contains the typed text, ignoring upper and lower case. An empty search SHALL list all cards.

#### Scenario: Searching
- **WHEN** the memory holds cards for `skew` and `standard deviation` and the reader types `dev`
- **THEN** only the card for `standard deviation` is listed

### Requirement: Progress
The page SHALL show how many cards are remembered in total, how many of them are word cards and definition cards, how many were downloaded this week (from Monday), and how many in each of the last six months.

#### Scenario: This week
- **WHEN** today is Thursday 22 October 2026 and cards were downloaded on 9, 19 and 22 October
- **THEN** the page says 3 cards in total and 2 this week, and 3 in October

### Requirement: Deleting a remembered card
The reader SHALL be able to delete a remembered card from the page, after confirming. A deleted card SHALL be gone from the memory: it is no longer listed or counted, and picking its word again in the reading page no longer shows it as an earlier card. Deleting SHALL NOT touch any deck or Anki.

#### Scenario: Deleting
- **WHEN** the reader deletes the remembered card for `skew` and later clicks `skew` in a text
- **THEN** a new card is made straight away, with no earlier card shown

### Requirement: A memory that cannot be read
If the memory cannot be read, the page SHALL say so and why, and SHALL show no cards.

#### Scenario: A damaged database
- **WHEN** the database file is not a SQLite database
- **THEN** the My cards page shows the reason and an empty list

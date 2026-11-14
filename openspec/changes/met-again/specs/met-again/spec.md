## ADDED Requirements

### Requirement: Meeting a card again
When a text is read or a file opened, each remembered card whose word or term is in the text, by the rules of the `known-words` capability, SHALL be recorded as met in that text, with the day. A card SHALL be recorded at most once per text: two texts are the same when their words are the same after tidying. The text a card was made from SHALL NOT count as meeting it again, whether the card was sent to Anki or downloaded, and whether that text is read before or after. A memory that cannot be read or written SHALL record nothing, and reading SHALL still work.

#### Scenario: A word met in a new text
- **WHEN** the memory has a word card for `skew` made from one text, and the reader reads a different text containing `skewed`
- **THEN** the card for `skew` has been met again in 1 text

#### Scenario: The same text twice
- **WHEN** the reader reads that second text again, on the same day or later
- **THEN** the card for `skew` has still been met again in 1 text

#### Scenario: The text the card came from
- **WHEN** the reader makes a card for `skew` from a text, sends it to Anki, and later opens the same text again
- **THEN** the card for `skew` has been met again in 0 texts

#### Scenario: Many places in one text
- **WHEN** a text contains `confounder` 40 times and the memory has a card for it
- **THEN** the card has been met again in 1 text

### Requirement: Where meetings are shown
My cards SHALL show, for each card met again in at least one text, `Met again in N texts, last on DATE`, with `1 text` for one. The card shown when pointing at an underlined word SHALL show the same line. Cards never met again SHALL show no such line.

#### Scenario: On My cards
- **WHEN** the card for `skew` was met again in two texts, last on 2026-11-14
- **THEN** My cards shows `Met again in 2 texts, last on 2026-11-14` with that card

#### Scenario: Never met again
- **WHEN** a card has not been met again
- **THEN** My cards shows no such line for it

### Requirement: Keeping meetings
Meetings SHALL be kept in the card memory, in a table of their own, so that the memory's layout is 3. A memory of layout 2 SHALL be brought to layout 3 when opened, keeping its cards. When the last card for a word or term is deleted, its meetings SHALL be deleted too.

#### Scenario: An existing memory
- **WHEN** sentmine opens a memory of layout 2 with 10 cards
- **THEN** the memory has layout 3 and still has the 10 cards

#### Scenario: Deleting a card
- **WHEN** the only card for `skew` is deleted on My cards
- **THEN** its meetings are deleted, and a new card for `skew` starts with none

## ADDED Requirements

### Requirement: Words with cards are underlined
When a text or PDF is shown, each word whose base form has a word card in the memory SHALL be underlined with a dotted line, wherever it appears, on pasted text and on a PDF's pages. A word picked in this session SHALL show as picked, not underlined. Words SHALL be matched by base form, as in the earlier-card check. A memory that cannot be read SHALL underline nothing, and reading SHALL still work. Definition terms SHALL NOT be underlined.

#### Scenario: A word with a card
- **WHEN** the memory has a word card for `skew` and the reader reads `Outliers can skew it considerably.`
- **THEN** `skew` is underlined and the other words are not

#### Scenario: Another form of the word
- **WHEN** the memory has a word card for `run` and the text contains `ran`
- **THEN** `ran` is underlined

#### Scenario: A definition term
- **WHEN** the memory has only a definition card for `variance`
- **THEN** `variance` is not underlined

#### Scenario: No memory
- **WHEN** the app runs without a card memory
- **THEN** no word is underlined and the text can be read and picked as before

### Requirement: Pointing at an underlined word shows its card
Pointing at an underlined word SHALL show the remembered card: its front and back as on the card, and the day it was made. Moving away SHALL hide it. Clicking the word SHALL do what clicking a word with an earlier card does.

#### Scenario: Pointing at a word
- **WHEN** the reader points at an underlined `skew` whose card was made on 2026-10-29
- **THEN** the page shows that card's front and back and `2026-10-29`

### Requirement: The reader is told how many card words a text has
The message after reading a text or a file SHALL end by saying how many different words of the text already have cards, when there is at least one.

#### Scenario: Three card words
- **WHEN** a pasted text contains three different words that have word cards
- **THEN** the message is `Text loaded. 3 words you have cards for are underlined.`

#### Scenario: One card word
- **WHEN** one word of a PDF has a card
- **THEN** the message ends `1 word you have a card for is underlined.`

### Requirement: New cards are underlined at once
After cards are sent to Anki or downloaded, the other places of their words in the text SHALL be underlined without reading the text again.

#### Scenario: After Send to Anki
- **WHEN** the reader makes a card for `skew`, sends it to Anki, and `skew` appears again later in the text
- **THEN** that later `skew` is underlined

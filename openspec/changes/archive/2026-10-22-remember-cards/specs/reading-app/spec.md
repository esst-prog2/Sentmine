## MODIFIED Requirements

### Requirement: The app runs on the reader's own computer
The reading app SHALL be a web page served only on the reader's own computer (address `127.0.0.1`). It SHALL NOT send the text or the cards to any other machine, and SHALL NOT need an account or an external service. It SHALL keep one text and its cards in memory. It SHALL write only two kinds of file: the deck the browser downloads, and the history of downloaded cards described by the `card-history` capability.

#### Scenario: Offline
- **WHEN** the machine has no network connection
- **THEN** the page opens and every feature works

### Requirement: Word cards
In Word mode the reader SHALL be able to click any word of the text. A click on a word that has no card SHALL make a word card whose front is the sentence the word is in and whose back is the word, lower-cased, followed by its base form in brackets when the base form differs from it (`sighed (sigh)`). A click on the very word that made a card SHALL remove that card. Words are found by the rules of the `passage-analysis` capability; a token containing a digit is not a word and cannot be clicked.

#### Scenario: Picking a word
- **WHEN** the text contains `Outliers can skew it considerably.` and the reader clicks `skew`
- **THEN** a card is made with the front `Outliers can skew it considerably.` and the back `skew`

#### Scenario: A word whose base form differs
- **WHEN** the reader clicks `sighed`
- **THEN** the back of its card is `sighed (sigh)`

#### Scenario: Unpicking a word
- **WHEN** the reader clicks the same `skew` again
- **THEN** its card is removed and the number of cards goes down by one

### Requirement: One card per word or term
The app SHALL NOT make a second card for a word or term that already has one in this session, and SHALL tell the reader that it already has a card. Two words are the same when their base forms match, as found by the `simplemma` package for English (`sigh` and `sighed`, `ran` and `run`); `hoped` and `hopped` are different words. Two terms are the same when they match ignoring upper and lower case and spacing. A word card and a definition card for the same text MAY both exist.

When a word or term has no card in this session but has one in the history, the app SHALL NOT make a card straight away. It SHALL show the earlier card, with its front, back and date, and let the reader either skip it, making no card, or make the card anyway. A card made anyway SHALL show in the preview that a card was made before, with the date.

#### Scenario: Second occurrence of a word
- **WHEN** `stubborn` has a card and the reader clicks another `stubborn` elsewhere in the text
- **THEN** no card is made, the number of cards stays the same, and a message says the word already has a card

#### Scenario: Another form of a word
- **WHEN** `sighed` has a card and the reader clicks `sigh`
- **THEN** no card is made

#### Scenario: An irregular form of a word
- **WHEN** `run` has a card and the reader clicks `ran`
- **THEN** no card is made

#### Scenario: Same term again
- **WHEN** `standard deviation` has a card and the reader makes a definition card for `Standard  Deviation`
- **THEN** no card is made

#### Scenario: A word with an earlier card
- **WHEN** the history holds a card for `skew` made on 9 October 2026 and the reader clicks `skewed`
- **THEN** no card is made yet, and the page shows the earlier card with its sentence, back and date, and the choice to skip or make it anyway

#### Scenario: Made anyway
- **WHEN** the reader chooses to make that card anyway
- **THEN** the card is made and the preview shows that a card was made before, on 9 October 2026

### Requirement: Download
Download SHALL give the reader an `.apkg` deck holding the cards exactly as the preview shows them, in the same order, and SHALL add them to the history. The file name SHALL be the deck name the reader gave, `new` by default, with `.apkg`. Every character of the name other than letters, digits, spaces, `-` and `_` SHALL become a space, runs of spaces SHALL become one, and a name left empty SHALL become `new`. With no cards, Download SHALL give no file, SHALL add nothing to the history, and SHALL say why.

#### Scenario: A deck name that is not a safe file name
- **WHEN** the reader names the deck `../../evil`
- **THEN** the file is `evil.apkg`

#### Scenario: Edited text is what is downloaded
- **WHEN** a card was edited in the preview and the deck is downloaded
- **THEN** the deck and the history hold the edited text, not the original

#### Scenario: No cards
- **WHEN** Download is pressed with no cards
- **THEN** no file is given, the history is unchanged, and a message says there are no cards yet

## MODIFIED Requirements

### Requirement: Word cards
The reader SHALL be able to click any word of the text. A click on a word that has no card SHALL make a card whose front is the word, lower-cased, followed by its base form in brackets when the base form differs from it (`sighed (sigh)`), and whose back is the sentence the word is in, with the word in bold. A click on the very word that made a card SHALL remove that card. Words are found by the rules of the `passage-analysis` capability; a token containing a digit is not a word and cannot be clicked.

#### Scenario: Picking a word
- **WHEN** the text contains `Outliers can skew it considerably.` and the reader clicks `skew`
- **THEN** a card is made with the front `skew` and the back `Outliers can skew it considerably.`

#### Scenario: A word whose base form differs
- **WHEN** the reader clicks `sighed`
- **THEN** the front of its card is `sighed (sigh)`

#### Scenario: Unpicking a word
- **WHEN** the reader clicks the same `skew` again
- **THEN** its card is removed and the number of cards goes down by one

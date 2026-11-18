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

### Requirement: Definition cards
A drag over a term of up to eight words, or the same words marked with the keyboard, SHALL make a card at once whose front is the term and whose back is the sentence the term is in (the sentences, when the term runs across two); no second drag SHALL be needed. A longer drag SHALL make no card and SHALL say to drag over the term only and use Add sentences for a longer passage. A passage of several sentences or paragraphs SHALL be made with Add sentences. A break between paragraphs inside the passage SHALL be kept; other runs of spaces SHALL become one space. An empty term SHALL be refused with a message.

#### Scenario: A two-sentence definition
- **WHEN** the reader drags over `standard deviation` in `The standard deviation measures how spread out a set of values is. It is the square root of the variance.`, then adds the second sentence with Add sentences
- **THEN** the card's front is `standard deviation` and its back is both sentences

#### Scenario: A definition across two paragraphs
- **WHEN** the passage holds a sentence from one paragraph and one from the next
- **THEN** the back of the card keeps the break between the two paragraphs

#### Scenario: Nothing marked
- **WHEN** the term is empty
- **THEN** no card is made and a message says what is missing

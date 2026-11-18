## MODIFIED Requirements

### Requirement: A definition card can be a cloze card
Each card SHALL be either a cloze card or a term → passage card, and the reader SHALL be able to switch it in the preview. A new card SHALL start as a term → passage card. A cloze card SHALL hide every place the term appears in the passage, as a whole word and ignoring case. Switching to cloze SHALL be refused with a message when the term is not in the passage. An edit that removes the term from the passage SHALL make the card a term → passage card.

#### Scenario: The term is in the passage
- **WHEN** the reader marks the term `standard deviation` and the passage `The standard deviation measures how spread out a set of values is.`, then presses Make it cloze
- **THEN** the card's front is `The [...] measures how spread out a set of values is.`

#### Scenario: A word card made cloze
- **WHEN** the reader clicks `skew` in `Polls skew young.` and presses Make it cloze
- **THEN** the card's front is `Polls [...] young.`

#### Scenario: A word that only contains the term
- **WHEN** the term is `variance` and the passage is `The covariance of two variables.`
- **THEN** Make it cloze is refused, since there is nothing to hide

#### Scenario: Switching
- **WHEN** the reader switches a cloze card to term → passage
- **THEN** its front is the term and its back is the passage with the term in bold

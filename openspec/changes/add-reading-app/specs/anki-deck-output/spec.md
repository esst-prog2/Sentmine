## ADDED Requirements

### Requirement: Definition card
A definition card SHALL have the term on the front and the marked passage on the back. On both sides `<`, `>` and `&` SHALL be escaped so the text displays as written, and nothing SHALL be put in bold. A line break in the text SHALL display as a line break on the card.

#### Scenario: Term and passage
- **WHEN** a definition card has the term `standard deviation` and the passage `It is the square root of the variance.`
- **THEN** the card front is `standard deviation` and the card back is that passage

#### Scenario: Special characters
- **WHEN** the passage is `x < y & y > z`
- **THEN** the card displays exactly that text

#### Scenario: Two paragraphs
- **WHEN** the passage has two paragraphs
- **THEN** the card back shows them as two paragraphs

## MODIFIED Requirements

### Requirement: Sentence splitting
The tool SHALL split the passage into sentences. A sentence ends at `.`, `!` or `?` only when it is followed by whitespace or the end of the text, optionally with closing quotation marks or brackets in between. The abbreviations `Mr.`, `Mrs.`, `Ms.`, `Dr.`, `St.`, `vs.`, `etc.`, `e.g.` and `i.e.` (case-insensitive) SHALL NOT end a sentence. A `!` or `?`, together with any closing quotation marks or brackets after it, SHALL NOT end a sentence when the next word starts with a lowercase letter. A sentence SHALL NOT end inside an open quotation: while the sentence so far has more opening than closing curly double quotation marks or guillemets, or an odd number of straight double quotation marks, an end mark does not end it. Single quotation marks SHALL NOT be counted. A blank line SHALL also end a sentence, including one inside an open quotation. Line breaks inside a sentence SHALL become a single space in the stored sentence text.

#### Scenario: Ordinary sentences
- **WHEN** the passage is `The dog sat. Its owner sighed.`
- **THEN** the tool reads 2 sentences

#### Scenario: Abbreviation does not end a sentence
- **WHEN** the passage is `Dr. Lee sighed.`
- **THEN** the tool reads 1 sentence, `Dr. Lee sighed.`

#### Scenario: Decimal number does not end a sentence
- **WHEN** the passage is `It cost 3.5 million.`
- **THEN** the tool reads 1 sentence

#### Scenario: Closing quote followed by a lowercase word
- **WHEN** the passage is `"Stop!" she said.`
- **THEN** the tool reads 1 sentence, `"Stop!" she said.`, and a second sentence is not started at the closing quote

#### Scenario: Closing quote followed by a capital letter
- **WHEN** the passage is `"Stop!" She ran.`
- **THEN** the tool reads 2 sentences, `"Stop!"` and `She ran.`, and the closing quote stays with the first

#### Scenario: A quote of several sentences is kept whole
- **WHEN** the passage is `She said: "Stop. Go back." Then she left.`
- **THEN** the tool reads 2 sentences, `She said: "Stop. Go back."` and `Then she left.`

#### Scenario: A quote from a real article
- **WHEN** the Guardian article in `spike/article.txt` is read and the word `restoke` is found
- **THEN** its sentence starts at `One cabinet minister told the Guardian:` and ends at the closing quotation mark and full stop after `restoke division`

#### Scenario: A quote that is never closed
- **WHEN** a paragraph opens a quotation and does not close it
- **THEN** the rest of that paragraph is one sentence and the next paragraph is split as usual

#### Scenario: Blank line ends a sentence
- **WHEN** a headline without a full stop is followed by a blank line and a paragraph
- **THEN** the headline is its own sentence

#### Scenario: Hard-wrapped sentence
- **WHEN** one sentence is spread over two lines of the file
- **THEN** its stored text has a single space where the line break was

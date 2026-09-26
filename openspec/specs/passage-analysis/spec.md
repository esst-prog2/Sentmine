# passage-analysis Specification

## Purpose

Turns a plain-text English passage into a list of new words, each tied to the sentence where it first appeared, and accounts for every word occurrence so the reader can trust the counts.

## Requirements

### Requirement: Sentence splitting
The tool SHALL split the passage into sentences. A sentence ends at `.`, `!` or `?` only when it is followed by whitespace or the end of the text, optionally with closing quotation marks or brackets in between. The abbreviations `Mr.`, `Mrs.`, `Ms.`, `Dr.`, `St.`, `vs.`, `etc.`, `e.g.` and `i.e.` (case-insensitive) SHALL NOT end a sentence. A `!` or `?`, together with any closing quotation marks or brackets after it, SHALL NOT end a sentence when the next word starts with a lowercase letter. A blank line SHALL also end a sentence. Line breaks inside a sentence SHALL become a single space in the stored sentence text.

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

#### Scenario: Blank line ends a sentence
- **WHEN** a headline without a full stop is followed by a blank line and a paragraph
- **THEN** the headline is its own sentence

#### Scenario: Hard-wrapped sentence
- **WHEN** one sentence is spread over two lines of the file
- **THEN** its stored text has a single space where the line break was

### Requirement: Word recognition
The tool SHALL find words in each sentence. A word is a run of letters of any alphabet, including internal apostrophes; a curly apostrophe SHALL be treated as a straight one, and quotation marks at the edges of a word SHALL be stripped. A hyphenated token SHALL be split into its parts, and each part SHALL be treated as a separate word. A whitespace-delimited token containing any digit SHALL NOT be a word and SHALL be counted as ignored. Words SHALL be compared in lower case.

#### Scenario: Contraction stays whole
- **WHEN** a sentence contains `don't`
- **THEN** it is one word, `don't`

#### Scenario: Curly apostrophe
- **WHEN** a sentence contains `don’t` written with a curly apostrophe
- **THEN** it is the same word as `don't`

#### Scenario: Hyphenated word
- **WHEN** a sentence contains `well-known`
- **THEN** `well` and `known` are two separate words

#### Scenario: Token with a digit
- **WHEN** a sentence contains `2026`, `3rd` or `COVID-19`
- **THEN** the token is counted as ignored and is never a card or a known word

#### Scenario: Accented letters
- **WHEN** a sentence contains `café`
- **THEN** it is the single word `café`

### Requirement: Every word occurrence is counted exactly once
The tool SHALL place every word occurrence in exactly one of four buckets: common (ignored), known, repeat, or card. For every run, the number of words read SHALL equal common plus known plus repeats plus cards.

#### Scenario: The demo passage
- **WHEN** the passage is `The stubborn old dog refused to move. Its owner sighed. She was resilient, but the dog was equally stubborn.` and `known.txt` holds `dog`, `old`, `move`, `owner`
- **THEN** the tool reads 3 sentences and 19 words
- **AND** 8 words are ignored as common (`the`, `to`, `its`, `she`, `was`, `but`, `the`, `was`)
- **AND** 5 word occurrences are already known (`old`, `dog`, `move`, `owner`, `dog`)
- **AND** 1 repeat is collapsed (the second `stubborn`)
- **AND** 5 cards are made, for `stubborn`, `refused`, `sighed`, `resilient` and `equally`, in the order they first appear
- **AND** 8 + 5 + 1 + 5 = 19

### Requirement: Common and too-short words are ignored
A word SHALL be ignored as common when it is in the built-in common-word list or is shorter than the minimum length, which defaults to 3 letters. This check SHALL use the word as written, not its stem, and SHALL come before the known-word check. Ignored words include the digit tokens above.

#### Scenario: Stopword
- **WHEN** a sentence contains `the`
- **THEN** `the` is ignored as common

#### Scenario: Minimum length
- **WHEN** the minimum length is 5 and the word `dog` is not in `known.txt`
- **THEN** `dog` is ignored, not made into a card

#### Scenario: Stopword that is also known
- **WHEN** `the` is listed in `known.txt`
- **THEN** it is counted as common, not as known

### Requirement: Known words
The tool SHALL read the optional known-words file with one word per line, ignoring blank lines and surrounding whitespace, and SHALL match it case-insensitively. A word occurrence SHALL count as known when its stem equals the stem of any known word. When comparing, a trailing `'s` SHALL be dropped.

#### Scenario: Inflected form of a known word
- **WHEN** `sigh` is in `known.txt` and the passage contains `sighed`
- **THEN** `sighed` counts as known and no card is made for it

#### Scenario: Known word is the inflected form
- **WHEN** `sighed` is in `known.txt` and the passage contains `sigh`
- **THEN** `sigh` counts as known

#### Scenario: Possessive
- **WHEN** `dog` is in `known.txt` and the passage contains `dog's`
- **THEN** `dog's` counts as known

#### Scenario: Case
- **WHEN** `Dog` is in `known.txt` and the passage contains `dog`
- **THEN** `dog` counts as known

### Requirement: Stem used only for matching
The tool SHALL compute a stem for each word and use it only to match known words and to collapse repeats. The stem SHALL be built by applying these rules in order to the lower-cased word: (1) drop a trailing `'s`; (2) a word ending in `ies` or `ied` and longer than 4 letters ends in `y` instead; (3) drop a trailing `ing` from a word longer than 5 letters and (4) drop a trailing `ed` from a word longer than 4 letters, in both cases only if a vowel remains, and then remove one of a doubled final `b`, `d`, `g`, `m`, `n`, `p`, `r` or `t`; (5) drop a trailing `s` from a word longer than 3 letters unless it ends in `ss`, `us` or `is`; (6) drop a final `e`. Irregular forms such as `ran` and `run` are not handled.

#### Scenario: Past tense matches base form
- **WHEN** the passage has `moved` and `known.txt` has `move`
- **THEN** the two have the same stem and `moved` counts as known

#### Scenario: Doubled consonant
- **WHEN** the passage has `stopped` and `known.txt` has `stop`
- **THEN** they have the same stem

#### Scenario: Words that must not be shortened
- **WHEN** the passage has `class`, `status`, `analysis`, `need` or `spring`
- **THEN** none is changed in a way that makes it match a different, shorter word

#### Scenario: Irregular forms are not matched
- **WHEN** the passage has `ran` and `known.txt` has `run`
- **THEN** `ran` is a new word

### Requirement: Repeats collapse to the first sentence
When a new word occurs more than once, counting occurrences whose stems are equal, the tool SHALL keep one card for it, use the first sentence it appeared in, and count each later occurrence as a repeat.

#### Scenario: Same word in two sentences
- **WHEN** `stubborn` appears in the first and the third sentence
- **THEN** one card is made and its sentence is the first one
- **AND** one repeat is counted

#### Scenario: Different forms of one word
- **WHEN** `sigh` appears in the first sentence and `sighed` in a later one, and neither is known
- **THEN** one card is made, showing the form and sentence that came first

### Requirement: Proper names get no special handling
The tool SHALL treat capitalised words like any other word. A name that is not common and not known SHALL become a card.

#### Scenario: A name
- **WHEN** the passage has `Anna sighed.` and `anna` is not known
- **THEN** `anna` becomes a card

## Why

Underlining words that already have cards leaves out definition cards, and for the reader's statistics course those are the cards that matter most: `confounder`, `Simpson’s reversal`, `backdoor criterion`. Meeting such a term again in a new chapter is exactly the moment to check whether its definition is still remembered.

## What Changes

- A definition term that has a card in the memory is underlined wherever it appears in a new text or PDF, as a whole: every word of `Simpson’s reversal`.
- Pointing at any word of an underlined term shows its card: the term, the passage and the day it was made.
- The message after reading counts words and terms: `2 words and 1 term you have cards for are underlined.`
- A term is found as whole words, ignoring upper and lower case, as cloze cards find a term in its passage. Other forms (a plural) are not found.
- Where a word card and a term overlap, the term is shown.

Not in this change: other forms of a term (`confounders`); terms broken across a page break in a PDF are found as in the text read from it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities
- `known-words`: definition terms are underlined too, and the message counts them.

## Impact

- `memory.py`: the latest definition card for each term.
- `reading.py`: the layout marks the words of each remembered term found in a sentence.
- `app.py`: the cards for the terms in the text, and the message.
- `web/index.html`: no change expected; a term's words carry the same mark as a word with a card.

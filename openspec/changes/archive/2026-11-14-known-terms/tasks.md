## 1. Terms

- [x] 1.1 `CardMemory.term_cards()`: the latest definition card for each term
- [x] 1.2 The layout marks every word of each remembered term found in a sentence (one pattern for all terms, whole words, ignoring case); a term wins over a word card
- [x] 1.3 The cards of the terms in the state, under their own keys; the message counts words and terms; verify each scenario with the test client

## 2. Check

- [x] 2.1 In headless Edge: a remembered term underlined on the course PDF and on pasted text, and its card shown when pointing; rerun the click and drag checks
- [x] 2.2 Measure the 166-page book with 50 remembered terms
- [x] 2.3 Run the whole suite and `openspec validate known-terms --strict`

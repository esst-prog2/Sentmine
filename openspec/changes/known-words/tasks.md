## 1. Which words have cards

- [x] 1.1 `CardMemory.word_cards()`: the latest word card for each base form; empty when the memory cannot be read
- [x] 1.2 `Session.layout()` marks word pieces with the base form of their remembered card; picked words are not marked; `base_form` cached
- [x] 1.3 `known_cards` in the state, and the count at the end of the message after reading a text or file; verify each scenario with the test client

## 2. The page

- [x] 2.1 Dotted underline on text and on PDF boxes; the card shown when pointing; verify in headless Edge on text and on a PDF, and rerun the click and drag checks

## 3. Wrap-up

- [x] 3.1 Measure the time to read the 166-page book before and after
- [x] 3.2 Run the whole suite and `openspec validate known-words --strict`
- [ ] 3.3 The reader reads a text with words they have cards for (needs the reader)

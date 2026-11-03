## 1. Notes

- [x] 1.1 `deck.Note` and the cloze note type; `write_notes` writes both and still takes (front, back) pairs; verify by reading the .apkg in tests
- [x] 1.2 `send_notes` makes either note type when missing and finds duplicates across both; verify with the fake AnkiConnect

## 2. Cards

- [x] 2.1 The `cloze` flag, the whole-word match, the default, the switch, and edits that remove the term; verify each scenario of "A definition card can be a cloze card"
- [x] 2.2 Cloze cards remembered as definitions; verify through My cards' search

## 3. The page

- [x] 3.1 `PUT /api/cards/<id>/cloze` and the switch on definition cards; verify with the test client, `node --check` and a screenshot

## 4. Wrap-up

- [x] 4.1 Run the whole suite and `openspec validate cloze-cards --strict`
- [ ] 4.2 Make a cloze card in the browser, send it to the reader's Anki and study it there (needs the reader)

## 1. Setup

- [x] 1.1 Add `flask` to the dependencies in `pyproject.toml` and include `web/*.html` as package data; verify `pip install -e .[dev]` succeeds and `import flask` works

## 2. Reading session

- [x] 2.1 Implement `tidy()` in `src/sentmine/reading.py` (paragraphs on blank lines, wrapped lines joined, spaces collapsed, empty paragraphs dropped); verify tests for each scenario of "Pasting and tidying a text"
- [x] 2.2 Implement `Session.load()` and `Session.layout()` (paragraphs, sentences, clickable words numbered within their sentence, digit tokens not clickable); verify a test on the README paragraph finds 3 sentences and that `skew` is a clickable word of the third
- [x] 2.3 Implement `Session.pick_word()` (add, remove on the same word, duplicate by stem); verify tests for the scenarios of "Word cards" and "One card per word or term"
- [x] 2.4 Implement `Session.add_definition()` (term and passage tidied, paragraph breaks kept, duplicate terms, empty refused); verify tests for the scenarios of "Definition cards"
- [x] 2.5 Implement `Session.edit()` and `Session.delete()`; verify tests for the scenarios of "Preview, edit and delete", including that a deleted word can be picked again

## 3. Deck

- [x] 3.1 Split `write_deck` so that `write_notes(notes, path)` writes any front/back pairs; verify the existing deck tests still pass unchanged
- [x] 3.2 Implement the HTML of each card side (word card front through `card_front`, other sides escaped with line breaks as `<br>`) and `Session.export()`; verify tests for the "Definition card" scenarios and that a deck read back holds the edited text in preview order
- [x] 3.3 Refuse an export with no cards; verify a test that no file is written and the message says there are no cards

## 4. Web server

- [x] 4.1 Implement `create_app()` in `src/sentmine/app.py` with the routes for the page, the state, loading a text, picking a word, adding a definition, editing, deleting and downloading; verify with Flask's test client that each returns the state and that problems come back as status 400 with a message
- [x] 4.2 Verify with the test client the whole README demo: load the paragraph, make the definition card and the word card, edit one, download, read the deck back and find exactly the two cards

## 5. The page

- [x] 5.1 Write `src/sentmine/web/index.html`: paste box, the text with clickable words, the Word / Definition switch, the two-step term-then-definition selection, the card count, the preview with edit and delete, the deck name and Download, and a line for messages; verify the page is served at `/` and its script has no syntax error

## 6. The command

- [x] 6.1 Make `sentmine` with no arguments start the app (port 8000 or the next free one up to 8010, address printed, browser opened) and leave every other call to the existing parser; verify tests that no arguments calls the app, that `sentmine --force` still exits with 2, and that all earlier command-line tests pass

## 7. Wrap-up

- [x] 7.1 Run the whole test suite and `openspec validate add-reading-app --strict`; verify both pass
- [x] 7.2 Start `sentmine` for real and fetch the page and the state over HTTP; verify both answer
- [ ] 7.3 Try the page by hand in a browser with the README paragraph: one definition card, one word card, an edit, a download, and an import into Anki (needs the reader; the agent cannot click in a browser)
- [x] 7.4 Update README section 6 (install and run) for the reading app; verify the commands in it work

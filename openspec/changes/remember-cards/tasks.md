## 1. Base forms

- [x] 1.1 Add `simplemma==2.0.0` to `pyproject.toml` and write `lemma.base_form(word)`; verify tests that `sighed` gives `sigh`, `ran` gives `run`, `children` gives `child`, and that `hoped` and `hopped` give different base forms

## 2. The history file

- [x] 2.1 Write `history.History` (read a JSON Lines file, find by kind and key, append on add, skip entries already there) and `default_history_path()` (`SENTMINE_HISTORY`, `%APPDATA%`, `~/.local/share`); verify tests for each scenario of "Where the history is kept", "What an entry holds", "Finding an earlier card" and the twice-downloaded deck
- [x] 2.2 Make a history that cannot be read report why, find nothing, add nothing and leave the file unchanged; verify a test for "A damaged file"

## 3. The reading session

- [ ] 3.1 Use base forms as the key of word cards and show the base form on the back when it differs; update the tests that expected the back to be the word alone; verify tests for "A word whose base form differs" and "An irregular form of a word"
- [ ] 3.2 Give `Session` an optional history; `pick_word` and `add_definition` answer `earlier` with the earlier entry, and with `anyway=True` make the card with a "made before" date; verify tests for "A word with an earlier card", "Made anyway", and the same for a definition card
- [ ] 3.3 `Session.export` returns the cards it wrote, and a session with a history adds them to it; verify tests for "Deleted before download", "Edited text is what is downloaded" and "No cards"

## 4. The app and the page

- [ ] 4.1 `serve()` opens the reader's history; the state carries the earlier card and a history warning; the download adds to the history and sends a warning header if adding fails; verify with the test client, using a temporary history file
- [ ] 4.2 The page shows the earlier card with Skip and Make it anyway, the "made before" note in the preview, and any history warning; verify the page script has no syntax error

## 5. Wrap-up

- [ ] 5.1 Run the whole suite and `openspec validate remember-cards --strict`; verify both pass and the first design still writes 103 cards from the spike article
- [ ] 5.2 Try it in the browser: make and download a card, start the app again, pick the same word in another form, and see the earlier card (needs the reader)

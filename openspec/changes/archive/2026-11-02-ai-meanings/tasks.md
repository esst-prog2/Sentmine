## 1. The model

- [x] 1.1 Write `meaning.py`: `find_api_key()` (variable, then `.env` in the user folder) and `suggest_meaning(word, sentence, key, post)`; verify with a fake `post` that only the word and sentence are sent, and tests for each failure of "When a request fails" and for an empty answer

## 2. The session and the app

- [x] 2.1 `Session.suggest(card_id, ask)`: word cards only, meaning on its own line under the word, a second press replaces it, a failure changes nothing; verify tests for "A meaning for a word", "Pressing it again", "A definition card" and "Editing a suggestion"
- [x] 2.2 `create_app(session, ask)`, `POST /api/cards/<id>/meaning`, `can_suggest` in the state; `serve()` builds the real `ask` when a key exists and never prints it; verify with the test client, including "No key"

## 3. The page

- [x] 3.1 The Suggest meaning button on word cards when `can_suggest`, showing that it is waiting; verify the script has no syntax error

## 4. Wrap-up

- [x] 4.1 Run the whole suite and `openspec validate ai-meanings --strict`; verify both pass, the tests make no network request, and the first design still writes 103 cards
- [x] 4.2 One real request through `suggest_meaning`; verify it returns a short explanation
- [x] 4.3 Try the button in the browser: suggest a meaning, edit it, download, import into Anki, and find it in My cards (needs the reader)

  Done by the reader on 2026-11-02: a meaning suggested for `applications`, downloaded, and imported into Anki (screenshots), and the card checked in the database. Editing a meaning before download is covered by a test; the reader did not report trying it.

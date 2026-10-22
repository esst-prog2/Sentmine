## 1. The database

- [x] 1.1 Write `memory.CardMemory` on SQLite: open or create `cards.db`, schema version 1 (table and index), `find`, `add` (once per card), and `default_memory_path()` (`SENTMINE_DATABASE`, `%APPDATA%`, `~/.local/share`); verify tests for "First use", "What an entry holds", finding by kind and key, and the same card stored once
- [x] 1.2 Schema version 2: copy `history.jsonl` once in one transaction, leave it unchanged, retry next start if it cannot be read; refuse a newer version; verify tests for each scenario of "Moving the old history file into the database" and "A newer database"
- [x] 1.3 A database that cannot be opened: report why, find nothing, refuse to add, leave the file unchanged; verify a test for "A damaged database"
- [x] 1.4 `search(text)`, `progress(today)` and `delete(id)`; verify tests for "Searching", "This week" and deleting

## 2. The reading app on the database

- [x] 2.1 `history.py` keeps only reading the old file; the session and `serve()` use `CardMemory`; verify every earlier test of remembering cards passes on the database
- [ ] 2.2 `GET /api/memory?q=` and `DELETE /api/memory/<id>`; verify with the test client, including "Deleting" (no earlier card afterwards) and the damaged database

## 3. The My cards page

- [ ] 3.1 Write `web/cards.html` (list, search as you type, progress, delete with confirmation, the memory warning) and link it from the reading page and back; verify both pages are served and their scripts have no syntax error

## 4. Wrap-up

- [ ] 4.1 Run the whole suite and `openspec validate memory-database --strict`; verify both pass and the first design still writes 103 cards from the spike article
- [ ] 4.2 Start the app for real with a temporary folder holding an old `history.jsonl`; verify over HTTP that its cards are in the database and on `/api/memory`
- [ ] 4.3 Try the My cards page in the browser: search, progress, delete one card, and pick its word again (needs the reader)

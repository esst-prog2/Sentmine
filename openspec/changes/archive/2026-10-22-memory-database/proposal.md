## Why

The reading app remembers downloaded cards in a plain text file (`history.jsonl`), read whole at every start. It can answer one question: is there a card for this word? The professor's question from the first review (issue #1) was what the tool would know about someone after a month, and the file cannot say: not which cards I have, not how many I made this week, and I cannot remove a card I deleted in Anki, so the app keeps warning about it.

A database is the right tool once the memory has to answer more than one question. The professor's session 7 slides list what one is for (data that outlives a run; finding things fast in a lot of data; changes that must not half-happen) and what it adds (a schema, migrations, backups).

## What Changes

- The card memory becomes a SQLite database, `cards.db`, in the same user folder as before. SQLite is part of Python: no new package, no server.
- The first time the new version starts, the cards in an existing `history.jsonl` are copied into the database. The old file is left as it was.
- The database has a schema version, so later changes to its layout can be migrated the same way.
- A new page, **My cards**, reachable from the reading page:
  - every remembered card, newest first, with its date;
  - a search box (word, term, sentence or back);
  - progress: cards in total, this week, and per month;
  - delete a remembered card, after a confirmation.
- Remembering on download, finding an earlier card, and Skip / Make it anyway work as before, now on the database.

Not in this change: AI meanings (the next change, which will store meanings in this database); editing a remembered card; search by meaning (a vector store); several readers or devices; reading old `.apkg` decks.

## Capabilities

### New Capabilities
- `my-cards`: the My cards page: listing, search, progress and delete.

### Modified Capabilities
- `card-history`: the memory is a SQLite database with a schema version; the old history file is moved into it once; a database that cannot be opened is reported, as the file was.

## Impact

- New: `src/sentmine/memory.py` (the database), `src/sentmine/web/cards.html` (the page), tests for both.
- Changed: `history.py` keeps only reading the old file, for the move; `reading.py` and `app.py` use the database; the reading page gets a link to My cards.
- The command-line tool of the first design is not touched.

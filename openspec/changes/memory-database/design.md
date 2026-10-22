## Context

`remember-cards` added a history of downloaded cards as a JSON Lines file, read whole at every start, with `find` and `add`. The reading session uses it to show an earlier card and to remember cards on download. Decisions behind this change are in `PLANNING_LOG.md`, 2026-10-22.

## Goals / Non-Goals

**Goals:** a memory that can be searched, counted and changed; a page that shows it; a safe move from the old file; behaviour of the reading page unchanged.

**Non-Goals:** several readers or devices; editing remembered cards; AI meanings (next change); search by meaning.

## Decisions

**SQLite through Python's own `sqlite3`.** One file, no server, no new dependency, a backup is a copy. *Alternatives* (from the session 7 slide): a document database or a hosted service would need a server and an account; a key-value store can only find by key, which the old file already did.

**One table.**

```
cards(id INTEGER PRIMARY KEY,
      kind TEXT NOT NULL CHECK (kind IN ('word','definition')),
      key TEXT NOT NULL, front TEXT NOT NULL, back TEXT NOT NULL,
      word TEXT NOT NULL DEFAULT '', made_on TEXT NOT NULL,
      UNIQUE (kind, key, front, back))
index on (kind, key)
```

`UNIQUE` replaces the old "skip entries already there" code: `INSERT OR IGNORE` does it. The index makes "is there an earlier card?" fast however many cards there are.

**Schema versions with `PRAGMA user_version`.** Version 1 creates the table and index. Version 2 copies `history.jsonl`. Each step runs in one transaction together with setting the version, so a step happens completely or not at all. A version above the app's is refused. The next change (AI meanings) will add version 3.

**The move from the old file is a migration step.** It reads the file with the existing reader (kept in `history.py`), inserts every card in one transaction, and leaves the file untouched. If the file is damaged, the step fails, the version stays at 1, and the next start tries again; the reader is told the file's path. `INSERT OR IGNORE` makes a repeated copy harmless anyway.

**A connection per operation.** The Flask development server may answer requests on different threads; a short-lived connection for each call avoids sharing one across threads. At this size, opening a connection costs nothing noticeable.

**Same interface for the session.** `CardMemory` has the `find`, `add` and `problem` the session already uses, plus `search`, `progress` and `delete` for the page. The session and the reading page change only in names.

**The page.** `cards.html`, a second static page like `index.html`, calling `GET /api/memory?q=` (cards and progress) and `DELETE /api/memory/<id>`. Search runs as the reader types. Progress is computed in SQL from `made_on`.

**Dates.** "This week" starts on Monday, by the computer's local date. Months are the last six calendar months including the current one.

## Risks / Trade-offs

- [A second copy of the app running at once] -> SQLite locks the file during each write; both copies stay consistent.
- [The old file is kept, so the cards exist twice on disk] -> Deliberate: nothing the reader made is deleted by an upgrade. They can delete `history.jsonl` once they are happy.
- [Deleting a card cannot be undone] -> The page asks for confirmation first; a copy of `cards.db` is a backup.
- [200 cards shown at most] -> The count says how many there are; search narrows the list.

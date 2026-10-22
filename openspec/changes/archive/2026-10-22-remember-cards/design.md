## Context

The reading app (`reading.py`, `app.py`, `web/index.html`) holds one text and its cards in memory and forgets them when it stops. Within a session, two word cards are the same when their stems match (`stem.py`, the first design's rules). The decisions behind this change are in `PLANNING_LOG.md`, dated 2026-10-17.

## Goals / Non-Goals

**Goals:**
- The app knows which words and terms already have a downloaded card, across sessions.
- Different forms of a word, including irregular ones, count as the same word.
- Everything testable without the reader's own files, a network or a browser.

**Non-Goals:**
- Reading old `.apkg` decks or the Anki collection.
- Telling which meaning of a word is meant (`saw` the verb or the tool): that needs the sentence, and is left for the AI change.
- Changing the first design's command-line tool.

## Decisions

**A JSON Lines file.** One JSON object per line, appended to. It is readable in any text editor, adding a card never rewrites the old entries, and a damaged line can be pointed to by number. About 300 bytes per card. *Alternative:* SQLite, which is faster to search, but the file is small and SQLite would hide the history from the reader.

**Where it lives.** `%APPDATA%\sentmine\history.jsonl` on Windows, `~/.local/share/sentmine/history.jsonl` elsewhere, or the file named by `SENTMINE_HISTORY`. The variable is how tests point the app at a temporary file.

**Who gets a history.** `Session()` and `create_app()` have no history unless one is passed in. Only `serve()`, the real command, passes the reader's history. A test can therefore never touch the reader's file by accident.

**Base forms in their own module.** `lemma.py` has one function, `base_form(word)`, that calls `simplemma.lemmatize(word, lang="en")` and lower-cases the result. The word key of a card and of a history entry is its base form. `stem.py` stays for the first design's command-line tool.

**The earlier card is a third answer.** `pick_word` and `add_definition` already answer `added`, `removed` or `duplicate`. They gain `earlier`: no card is made, and the earlier entry is returned. Both take `anyway=False`; with `anyway=True` the history is not checked and the new card keeps the earlier entry's date for its "made before" note. The page shows the earlier card with two buttons; *Make it anyway* sends the same click again with `anyway: true`.

**Adding on download.** The download route writes the deck, adds its cards to the history, then sends the file. If adding fails, the deck is still sent and a response header carries a warning, which the page shows. An entry that is already in the file, with the same kind, key, front and back, is not added again.

**Reading the history once.** It is read when the app starts and kept in memory; downloads append both to memory and to the file. A file that cannot be read gives a history marked as broken: it finds nothing, adds nothing, and the page shows why. The file is never rewritten or deleted.

## Risks / Trade-offs

- [The base form is chosen without the sentence: `saw` becomes `see`, `leaves` becomes `leave`] -> A wrong match shows the earlier card and the reader can make the new one anyway; the AI change can use the sentence later.
- [A card deleted in Anki stays in the history] -> The reader can still make it anyway. Reading Anki itself is a later change.
- [Two copies of the app running at once could both append] -> Each appends whole lines; both survive. Not worth more for one reader.
- [The history is personal data] -> It is kept in the user folder, never in the repository; `.env`-style rules are not needed because it is outside the project.
- [simplemma adds about 19 MB and 0.2 s to the first word] -> Measured on 2026-10-17; acceptable for a program that starts once per reading session.

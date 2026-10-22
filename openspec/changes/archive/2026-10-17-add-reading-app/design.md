## Context

sentmine is a Python command-line tool: `split_sentences`, `find_words`, `stem`, `analyse` (the word filter), `card_front`, and a `.apkg` writer built on `genanki`, with 225 tests. The Homework 4 spike showed that the word filter leaves the reader sorting cards by hand (4 of 103 cards were really new). This change adds a page where the reader chooses instead. The decisions behind it are in `PLANNING_LOG.md`, dated 2026-10-09.

## Goals / Non-Goals

**Goals:**
- A first version that is useful alone: paste, pick, check, download.
- All card logic in Python, where it can be tested without a browser.
- Reuse the tested sentence, word, stem and deck code unchanged.

**Non-Goals:**
- PDFs, links, AI suggestions, AnkiConnect, a browser extension (later changes).
- Several readers or several texts at once; saving between sessions.
- Removing the first design's command-line tool.

## Decisions

**Three layers.** `reading.py` holds a `Session`: the tidied text, its sentences, and the list of cards, with one method per thing the reader can do. `app.py` is a thin Flask layer: each route calls one `Session` method and returns the whole state as JSON. `web/index.html` is one page with its script and styles inline; after every action it redraws from the state it got back. The page decides nothing about cards, so the behaviour in the specs is tested through `Session` and through Flask's test client.
- Alternative: build the cards in the page's script. Rejected: the rules (sentence, bold, stems, duplicates) already exist in Python with tests, and script in a page is the part I cannot test here.

**Flask.** One small dependency, a built-in test client, and it serves a page with one command.
- Alternative: Python's own `http.server`, no dependency. Rejected: more hand-written request handling and no test client.

**State in memory, one session.** The app is for one reader on one computer. A new text replaces the old one and its cards; the page asks first.

**How the page names what was picked.** A word is named by two numbers: its sentence, counted through the whole text, and its place among the clickable words of that sentence. A term and a passage are sent as the selected text itself; the server tidies the spacing. Sending text avoids mapping a browser selection back to positions in the text.

**What makes two cards the same.** Word cards: the stem of the word. Definition cards: the term, lower-cased with single spaces. A click on the exact word that made a card removes it; a click on any other word with the same stem is a duplicate and changes nothing.

**Cards hold plain text.** A card stores its front and back as plain text, plus, for a word card, the word to put in bold. The HTML for Anki and for the preview is made from these when needed (`card_front` for word cards; escape and turn line breaks into `<br>` for the rest). Editing therefore never involves HTML.

**Deck writing.** `write_deck` is split: a new `write_notes(notes, path)` writes any list of front/back HTML pairs, and `write_deck` calls it. The note type and its id stay the same, so Anki treats old and new decks alike. For a download the deck is written into a temporary folder and its bytes are sent to the browser.

**The command.** `sentmine` with no arguments starts the app; anything else goes to the existing argument parser. Port 8000, or the next free one up to 8010.

## Risks / Trade-offs

- [The page's script is not covered by automated tests] -> The script only sends clicks and redraws; every rule is tested in Python. The page must be tried by hand in a browser before the change is called done (task 7.3).
- [A selection in the browser may carry odd spacing] -> The server collapses spaces and keeps only paragraph breaks; the preview shows the result and it can be edited.
- [A pasted bullet list without blank lines runs together] -> Accepted for the first version; visible in the page and fixable in the preview.
- [No arguments used to be an error and now starts a server] -> Deliberate; the one test that pinned the old behaviour is changed and the spec is updated.
- [Closing the terminal or pasting a new text loses unsaved cards] -> The page asks before replacing a text; saving between sessions is a later change.

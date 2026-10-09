## Why

The first design guessed which words were new to me from a list of words I know. I measured it on a real Guardian article (the Homework 4 spike, in `spike/`): of 103 cards it made, 4 were really new words, 64 were words I already knew and 35 were names or junk. I still sorted the cards by hand, so the guess saved me nothing.

The reader knows what is new to them the moment they meet it. sentmine should therefore let me choose what becomes a card while I read, and do the tedious part for me: take the sentence, build the card, and write the deck. The same page also serves my course reading, where what I need to learn is a term and its definition, not a single word.

## What Changes

- Add a reading app: a web page served on my own computer, started by running `sentmine` with no arguments.
- Paste a text into the page; it is tidied (wrapped lines joined, extra spaces and blank lines removed) and shown with every word clickable.
- Word mode: a click on a word makes a word card (front: its sentence with the word in bold; back: the word). A second click on the same word removes the card.
- Definition mode: select a term, then mark the passage that defines it, of any length. This makes a definition card (front: the term; back: the passage).
- One card per word or term: picking one that already has a card makes no second card and says so.
- A preview shows every card; each can be edited or deleted before the deck is written. The header shows the number of cards.
- Download writes an Anki `.apkg` deck of the cards as they appear in the preview; with no cards it writes nothing and says why.
- **BREAKING**: `sentmine` with no arguments used to exit with code 2; it now starts the reading app. `sentmine PASSAGE ...` is unchanged.
- Add Flask as a dependency.

Deliberately **not** in this change (later changes, in this order): loading a PDF that contains text; AI suggestions for a word's meaning or a term's definition; reading scanned PDF pages with AI; loading an article from a web link; sending cards straight into Anki (AnkiConnect). Also not in this change: a browser extension, remembering cards between sessions, highlighting probably-new words from a known-words list, languages written without spaces, audio, images, formulas, a phone app.

## Capabilities

### New Capabilities
- `reading-app`: the reading page - starting it, pasting and tidying a text, making word cards and definition cards, the one-card rule, the preview with edit and delete, the card count, and the download.

### Modified Capabilities
- `anki-deck-output`: adds the definition card (term on the front, marked passage on the back) next to the word card.
- `command-line`: `PASSAGE` is no longer required; with no arguments the command starts the reading app.

## Impact

- New code: `src/sentmine/reading.py` (the reading session), `src/sentmine/app.py` (the web server), `src/sentmine/web/index.html` (the page).
- Changed code: `src/sentmine/deck.py` (write any front/back pairs), `src/sentmine/cli.py` (no arguments starts the app), `pyproject.toml` (Flask, the page as package data).
- Reused unchanged: sentence splitting, word finding, the stem rules, the `.apkg` writer.
- One existing test changes on purpose: no arguments no longer exits with 2.
- The first design's command-line tool, its known-words filter and its tests stay; nothing is removed in this change.

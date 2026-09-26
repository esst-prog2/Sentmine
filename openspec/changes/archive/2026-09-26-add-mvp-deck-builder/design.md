## Context

sentmine is a new, empty Python project; the repository holds only the README and OpenSpec setup. See proposal.md for motivation and scope, and the three specs (`passage-analysis`, `anki-deck-output`, `command-line`) for the required behavior. This document covers how to build it.

Constraints from the planning log: Python with the `genanki` library as the single dependency; no network at run time; the common-word list is a text file copied into the repo; the stem is only a matching key.

## Goals / Non-Goals

**Goals:**
- Small, readable modules where each spec requirement maps to one place in the code, so each rule can be tested on its own.
- One pure function from text to a result (counts and cards), separate from file and deck handling, so the demo numbers can be tested without touching disk or Anki.
- A deck that Anki imports without error.

**Non-Goals:**
- Performance tuning: a passage is at most a few thousand words and the run should take well under a second.
- A plugin or configuration system, or a library API meant for other programs.
- Anything on the proposal's deferred list.

## Decisions

### Shape: a pipeline of small pure steps

```
passage text
   |
   v
split_sentences  ->  [sentence]
   |
   v
find_words       ->  [(word, sentence_index)]     (hyphen split, digit tokens marked ignored)
   |
   v
classify         ->  bucket per occurrence:  common | known | repeat | card
   |                 (uses stopwords, min_len, known stems, stem())
   v
Analysis { sentences, words, common, known, repeats, cards[(word, sentence)] }
   |
   v
build_cards -> deck file (genanki)      summary line (cli)
```

`analyse(text, known_words, min_len) -> Analysis` is pure: no file access, no printing. The command-line layer reads files, calls it, writes the deck, prints the summary, and maps failures to exit code 2. **Why:** the counting rule `total = common + known + repeats + cards` and the demo numbers are the heart of the spec and can be checked with plain strings in tests. **Alternative:** one script that reads, analyses and writes as it goes - shorter, but the counting rules could only be tested through files and the deck.

### Layout

```
pyproject.toml            package metadata, dependency genanki, script "sentmine"
src/sentmine/
  sentences.py            split_sentences
  words.py                find_words (tokens, apostrophes, hyphens, digits)
  stem.py                 stem() - the six rules, in spec order
  analyse.py              analyse() and the Analysis result; stopword loading
  deck.py                 cards -> .apkg (front HTML, bold, escaping)
  cli.py                  arguments, file handling, summary, exit codes
  data/stopwords.txt      the 198 words, with an attribution line at the top
tests/                    one test file per module, plus an end-to-end test
```

The stopword file is read with `importlib.resources` so it works after installation, not only from a checkout. Lines starting with `#` in it are comments, so the attribution line does not become a stopword.

### Command line with `argparse`
The standard library's `argparse` already exits with code 2 on invalid arguments (for example `--min-len abc`), which is the code the spec wants. I set `--min-len` to a custom type that rejects values below 1. **Alternative:** `click` or `typer` - nicer, but a second dependency for no gain.

### Reading files
Files are read as UTF-8, accepting an optional byte-order mark. A file that cannot be read or decoded counts as "unreadable" and gives exit code 2 with a message. Files are opened read-only, so the "never modified" rule holds by construction. The deck is checked for existence before any work is written, and is written last, so a failed run leaves nothing behind.

### Stems are computed once
The known-words file is stemmed when it is loaded, into a set. Each word occurrence is stemmed once while classifying. The repeat check keeps a set of stems already turned into cards. **Why:** matching becomes a set lookup and the stem rules live in one function.

### Card front: escape first, then bold
The sentence is HTML-escaped first, then bold tags are added around whole-word matches of the card word (case-insensitive, `\b`-style boundaries that treat an apostrophe inside a word as part of it). Doing it in this order means the added tags are never escaped and the sentence text never contains raw markup. **Alternative:** bold first, then escape - would turn the tags into visible text.

### Anki deck details (`genanki`)
- One note type with two fields, Front and Back, and one card template that shows Front and, after the flip, Back. The model id is a fixed constant written in the code, because Anki identifies note types by id.
- The deck id is derived from the deck's file name with a stable hash, so importing the same deck name again updates the same deck instead of creating a new one.
- Each note's id is derived from its word and sentence, so importing the same card twice does not create a duplicate.
- **Verification:** an automated test opens the written `.apkg` (a zip holding an SQLite file), and checks the note count and the field text. A manual import into Anki is done once before calling the change finished, because that is the only test of "Anki does not silently reject it".

### Tests
`pytest`, as a development dependency. Every scenario in the specs becomes a test, named after the scenario. The demo passage, `known.txt` and the expected numbers (3 / 19 / 8 / 5 / 1 / 5) are fixtures shared by the analysis, deck and command-line tests, so the demo cannot drift out of sync with the specs.

### Python version
Python 3.10 or newer. Nothing in the design needs newer features, and this keeps the tool usable on older machines. The development machine has 3.14.

### Summary when nothing is new
When no new word remains, the counts part of the summary is still printed to standard output, the "Wrote ..." part is left out, and the message on standard error says no new word remains.

## Risks / Trade-offs

- **Dropping a final `e` merges real word pairs** (`bare`/`bar`, `hope`/`hop`), which could hide a new word behind a known one → accepted by the user; the spec's stem requirement lists the rules, so switching to candidate-set matching later is a change to one function with unchanged tests.
- **Sentence splitting is rule-based** and will mis-split unlisted abbreviations and initials (`Prof.`, `J. K. Rowling`) → produces a short, visible card, not a hidden one; the abbreviation list is a constant that is easy to extend.
- **Proper names become cards** → visible; the user adds them to `known.txt`.
- **Anki might reject the deck** even though the automated checks pass → the manual import test in the task list, and using `genanki` rather than hand-writing the file format.
- **The stopword list has no explicit licence** in the NLTK corpus README (it derives from the Snowball list) → the attribution line is kept with the file; fine for a personal course project, to be revisited if the project is ever published or distributed.
- **A few words in the 198-word list are content words for a learner** (for example `not`, `down`, `off`) → they are simply not offered as cards; the list is a plain text file the user can edit.
- **Words already carded in earlier runs come back** unless added to `known.txt` → accepted; the summary lists them so they can be pasted in.

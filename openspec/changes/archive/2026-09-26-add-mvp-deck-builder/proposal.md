## Why

I learn English by reading, and words I meet inside a real sentence stick far better than words on a list. Today, turning an article into Anki cards means picking words by hand, hunting for their sentences, and building cards one at a time. sentmine should do this in one command: read a passage, find the words that are new to me, and write an Anki deck where each new word sits in the sentence it came from.

The README describes the tool but is not yet precise enough to build from: its demo numbers do not add up (it claims 2 sentences, 16 words, 2 cards; the rules give 3 sentences, 19 words, 5 cards), and several rules were left open. This change fixes those gaps and defines the first working version.

## What Changes

- Add a `sentmine` command-line tool (Python) that reads a plain-text English passage and writes an Anki `.apkg` deck with one card per new word.
- Classify every word occurrence into exactly one bucket - common/ignored, already-known, repeat, or card - so that `total = common + known + repeats + cards`.
- Decide "new" with a built-in common-word list (NLTK English stopwords, copied into the repo), a minimum word length, and an optional `--known` file matched by a simple stem.
- Build cards whose front is the source sentence (HTML-escaped, the word in bold) and whose back is the word as it appeared, lower-cased.
- Print a one-line summary with the counts and the words that got cards; exit 0 when at least one card is written, exit 2 with a message otherwise.
- Never modify `passage.txt` or `known.txt`; refuse to overwrite an existing deck unless `--force` is given.
- Correct the README demo and wording to match these rules (done as a follow-up step, not part of the spec).

Deliberately **not** in this change (deferred): the `clean.html` report and `--report` flag, irregular forms (ran/run), skipping proper names, an automatic `--learned` flag, non-English text, definitions or translations, audio or images, editing existing decks, GUI, AnkiConnect, and reading PDF/EPUB.

## Capabilities

### New Capabilities
- `passage-analysis`: splitting a passage into sentences and words, and classifying each word occurrence as common, known, repeat, or card, with a stem used only for matching.
- `anki-deck-output`: building one card per new word (sentence front with the word in bold, word back) and writing a valid `.apkg` deck.
- `command-line`: the `sentmine` arguments, the one-line summary, the exit codes, and the rule that input files are never modified.

### Modified Capabilities

None. There are no existing specs.

## Impact

- New Python package and `sentmine` entry point; new tests.
- New data file: the 198-word common-word list, with an attribution line (source: NLTK English stopwords, derived from the Snowball list).
- One runtime dependency: `genanki`. The tool needs no network, account, or API.
- README changes later: demo numbers, "no external dependencies" wording, card-back wording, and removal of `--report` from the demo command.
- Decisions behind this change are recorded in `PLANNING_LOG.md`.

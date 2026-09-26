## 1. Project setup

- [x] 1.1 Create `pyproject.toml` (Python >= 3.10, dependency `genanki`, dev dependency `pytest`, console script `sentmine`) and the `src/sentmine/` and `tests/` folders; verify `pip install -e .[dev]` succeeds and `sentmine --help` runs
- [x] 1.2 Copy the 198-word NLTK English stopword list into `src/sentmine/data/stopwords.txt` with an attribution line as a `#` comment; verify a test loads it and finds 198 words, that `the`, `to`, `its`, `she`, `was`, `but` are in it, and that `equally`, `refused`, `old`, `dog`, `move`, `owner` are not
- [x] 1.3 Create the shared demo fixtures (passage, `known.txt`, expected counts 3 / 19 / 8 / 5 / 1 / 5 and the five card words in order) in `tests/`; verify they are imported by a placeholder test

## 2. Sentences and words

- [x] 2.1 Implement `split_sentences` (end marks, closing quotes, abbreviation list, blank lines, line breaks become a space); verify tests for each scenario in the sentence-splitting requirement pass
- [x] 2.2 Implement `find_words` (letters of any alphabet, internal and curly apostrophes, edge quotes stripped, hyphen split, digit tokens marked ignored); verify tests for each scenario in the word-recognition requirement pass

## 3. Stemming

- [x] 3.1 Implement `stem()` with the six rules in spec order; verify tests for `sighed`/`sigh`, `moved`/`move`, `stopped`/`stop`, `studied`/`study`, `dogs`/`dog`, that `class`, `status`, `analysis`, `need`, `spring` are not shortened into a different word, and that `ran` does not match `run`

## 4. Analysis and counting

- [x] 4.1 Implement loading of the known-words file (one word per line, blank lines ignored, case-insensitive, stemmed into a set, trailing `'s` dropped); verify tests for the known-word scenarios
- [x] 4.2 Implement `analyse(text, known_words, min_len)` with the four buckets, check order (common or too short, then known, then repeat or card), repeats collapsing to the first sentence, and capitalised words treated like any other; verify the demo fixture gives 3 / 19 / 8 / 5 / 1 / 5 with cards in first-appearance order
- [x] 4.3 Add a test that for a range of passages `words == common + known + repeats + cards` always holds, and tests for `--min-len 5` on `dog`, a stopword listed in `known.txt`, and the name `Anna`

## 5. Deck

- [x] 5.1 Implement the card front (escape `<`, `>`, `&` first, then bold every whole-word occurrence, case kept) and the card back (word as written, lower-cased); verify tests for the scenarios: twice in one sentence, capital letter kept, `AT&T said x < y.`, `dog` inside `dogged` not bold
- [x] 5.2 Implement writing the `.apkg` with `genanki` (fixed model id, deck id from the deck name, note id from word and sentence); verify a test opens the written file, counts the notes, and checks the front and back text of `stubborn`
- [x] 5.3 Import the deck produced from the demo into Anki by hand; verify the import succeeds and shows 5 new cards, and note the Anki version in the change notes
  - Done 2026-09-26 with Anki's own importer (the `anki` Python library, version 26.9.3), not the desktop app: the demo deck imported as 5 new notes and 5 cards in a deck named `new`, and importing it a second time gave 0 new and 5 duplicates.
  - Confirmed 2026-09-26 by the user in the Anki desktop app (Anki 26.8.1, from the installed program's file version): the import overview said "5 notes found in file" and "5 new notes imported", and all 5 rows showed status Added.

## 6. Command line

- [x] 6.1 Implement `cli.py` arguments and defaults (`PASSAGE`, `--known`, `--deck` defaulting to the passage name with `.apkg`, `--min-len` whole number >= 1, `--force`, no `--report`); verify tests for the default deck name and for `--min-len abc` exiting with 2
- [x] 6.2 Implement the summary line and exit 0 on success; verify the demo run prints the counts and the five words in order, and exits 0
- [x] 6.3 Implement every exit-2 case (missing or unreadable passage, missing `--known`, no new word with the counts still printed and no deck written, deck exists without `--force`, deck path cannot be written); verify a test for each, and that nothing is written in each case
- [x] 6.4 Verify with a test that the passage and known files are byte-for-byte unchanged after a successful run and after each failing run, and that `--force` replaces an existing deck

## 7. Wrap-up

- [x] 7.1 Run the whole test suite and `openspec validate add-mvp-deck-builder --strict`; verify both pass
- [x] 7.2 Run the demo command from a clean checkout with the README passage and `known.txt`; verify the output matches the corrected summary exactly
- [x] 7.3 Update the README (corrected demo numbers and word list, no `--report` in the demo command, card back is the word as written, "no network, account or API" instead of "no external dependencies", install and run instructions); verify the README demo output matches what 7.2 printed

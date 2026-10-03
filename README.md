# sentmine

A tiny command-line tool that reads an English passage I just finished,
finds the words that are new to me, and makes an Anki card for each one -
showing that word inside the real sentence it appeared in.

## 1. The demo

I am learning English by reading. I finish an article, copy the text into
a file called `passage.txt`, and it looks like this:

```
The stubborn old dog refused to move. Its owner sighed.
She was resilient, but the dog was equally stubborn.
```

I already keep a file, `known.txt`, of words I have learned before, one
per line - it contains `dog`, `old`, `move`, `owner`. Common words like
"the", "was", "to" I never bother listing, because the tool ignores them
by default. I type:

```
sentmine passage.txt --known known.txt --deck new.apkg
```

In under a second it prints one line:

```
Read 3 sentences, 19 words. 8 common words ignored, 5 already-known skipped, 1 repeat collapsed. Wrote 5 new cards to new.apkg: stubborn, refused, sighed, resilient, equally.
```

Every word in the passage is counted exactly once, so the numbers add up:
8 common + 5 already-known + 1 repeat + 5 cards = 19 words. `stubborn`
appears twice, so it is collapsed to one card using its FIRST sentence. The
five words are listed in the order they first appear. For `stubborn`, the
card's front is the real sentence with the word in bold:

```
front:  The stubborn old dog refused to move.   (stubborn in bold)
back:   stubborn
```

I import `new.apkg` into Anki, and my new cards are there - each word living
inside a sentence I actually read. Words I already made cards for last week
come back as new next time, so I paste the words from that line into
`known.txt` myself.

`known.txt` should hold my own vocabulary, not a general word list. In the
spike (see `spike/`), a 3000-word Oxford list left 77 of 126 cards on a
Guardian article as words I already knew, while only 16 were actually new to
me. Names and junk (33 of 126) are not filtered yet, so expect them as cards.

## 2. The shape

```
in       passage.txt   a plain-text English passage (UTF-8), any length
         --known FILE   an optional file of words I already know, one
                        per line; matched case-insensitively and by a
                        simple stem, so `sigh` also covers `sighed`
         --min-len N    optional: ignore words shorter than N letters
                        (default 3), on top of the built-in common-word
                        list (198 words)
         --deck FILE    optional: where to write the deck (default: the
                        passage name with .apkg, in the current folder)
         --force        optional: replace the deck if it already exists
out      new.apkg      an Anki-importable deck, one card per NEW word;
                        front = the sentence containing it with the word
                        in bold, back = the word as it appeared in the
                        sentence, lower-cased
         stdout        one summary line: sentences and words read,
                        counts for common-ignored, already-known,
                        repeats-collapsed, and the cards written with
                        their words
on disk  the deck sits where I asked; passage.txt and known.txt are
         never modified
exit     0 when at least one card is written; 2 when nothing is written,
         with a message on stderr naming the problem: the passage or
         known file is missing or unreadable, no new word remains, the
         deck already exists (and no --force) or cannot be written, or
         an option is invalid
```

## 3. The size

**First useful version**

- read a plain-text English passage from a file
- split it into sentences (on `.`, `!`, `?`) and into words (on spaces
  and punctuation) - trivial for English because words are space-separated
- lower-case and strip punctuation from each word; compare words by a
  simple stem for common endings (plural -s, past -ed, -ing) so "sighed"
  and "sigh" are not two cards. The stem is only used for matching - the
  card shows the word as it appeared
- decide "new": a word is new unless it is in the built-in common-word
  (stopword) list, is shorter than `--min-len`, contains a digit, or
  appears in `--known`
- collapse repeats: if a new word occurs more than once, keep one card and
  use the FIRST sentence it appeared in
- build one Anki card per new word: front is that sentence with the word
  wrapped in bold, back is the word as it appeared, lower-cased
- build a valid `.apkg` deck from those cards
- print a one-line summary with each count and the words that got cards
- never modify passage.txt or known.txt; refuse to overwrite an existing
  `.apkg` unless `--force` is given

**Not this term**

- any non-English language, especially Chinese or Japanese, because those
  need word-segmentation (no spaces between words) - a hard, separate
  problem; English's spaces are exactly what makes this tool feasible now
- looking up or generating a definition/translation for the word - the
  card teaches through context (the sentence), which is the whole point;
  adding meanings would need a dictionary or AI and is deferred
- real lemmatization or part-of-speech analysis (e.g. "ran" → "run",
  "better" → "good"); the first version handles only simple -s/-ed/-ing
  endings and accepts it will occasionally keep two forms of one word
- the `clean.html` report (each new word, its sentence, and every ignored
  or skipped word with the reason) - planned for the next change
- skipping proper names: a name becomes a card like any other word, and I
  add it to `known.txt`
- remembering the words I already made cards for: I paste them into
  `known.txt` myself for now
- audio, images, phonetics, or example sentences beyond the one mined
- editing, merging, or reading existing `.apkg` decks
- a GUI, AnkiConnect, AnkiWeb sync, or reading PDFs/EPUBs directly
  (I paste plain text; extracting text from documents is out of scope)

## 4. How we would know it works

- Given the three-sentence passage above with `known.txt` holding
  `dog, old, move, owner`, exactly five cards are written - `stubborn`,
  `refused`, `sighed`, `resilient`, `equally`, in that order - and the
  summary counts are 3 sentences, 19 words, 8 common, 5 known, 1 repeat,
  5 cards, which add up: 8 + 5 + 1 + 5 = 19.
- Given `stubborn` appearing in two sentences, only one card is written
  and its front is the FIRST sentence; the summary says `1 repeat
  collapsed`.
- Given the word `stubborn` as a new word, its card front is the exact
  source sentence with `stubborn` in bold and nothing else altered (apart
  from escaping `<`, `>` and `&`, and a line break inside the sentence
  becoming one space); the back is `stubborn`.
- Given `sighed` in the text and `sigh` already in `known.txt` (or vice
  versa), the stem matching means no card is written for it and it
  counts as already-known.
- Given only common words and known words in a passage, no deck is written
  and the run exits 2 with a message; the counts are still printed.
- Given `--min-len 5`, the word `dog` is ignored as too short even if it
  is not in known.txt.
- Given a missing or unreadable input file, the run exits 2 with a clear
  message and writes nothing.
- Given an existing output path, the run refuses and exits 2 unless
  `--force`; passage.txt and known.txt are unchanged in every case.
- Given the produced `.apkg`, importing it into Anki succeeds and the card
  count matches `Wrote N new cards`.

## 5. What could stop this

No network, account, or API. The tool handles no personal data. It reads and writes only local files, and the common-word list ships within the tool itself. It needs one Python library, `genanki`, to write the deck.

The core design is the choice of English. Chinese would first require segmenting words with no spaces between them - a hard, error-prone problem. English separates words with spaces, making the split reliable and reducing this from a research project to a weekend tool. The cost, stated above, is the absence of real lemmatization: "run" and "ran" may produce two cards. This is mitigated by tests covering the common -s/-ed/-ing cases; a stray duplicate is a minor, visible flaw, not a failure. The stem rules can also join two real words that differ only by a final "e" (`hop` and `hope`), which would hide a new word behind a known one - rare, and the price of keeping the rules simple.

The .apkg format is the second risk: producing a file that Anki silently rejects. This is defended by the final test above - a genuine import into Anki must succeed, verified by hand and against the genanki library's round-trip.

The deeper risk is that the code is thin. Splitting text and packaging an .apkg is modest work that an AI largely automates. The value lies instead in the fit to how I study: I learn English by reading, I meet new words in real sentences, and a word recalled within its sentence is retained far better than one in isolation. The --known file prevents the tool from burying me in words I already have. Should the cards prove no more useful than plain word lists, the premise was wrong — but sentence mining is a method serious learners already rely on.

## 6. Install and run

Needs Python 3.10 or newer.

```
pip install .                        # installs sentmine and genanki
sentmine passage.txt --known known.txt --deck new.apkg
```

To work on it and run the tests: `pip install -e ".[dev]"`, then `pytest`.

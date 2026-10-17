## Why

The reading app forgets everything when it is closed. A word I made a card for last week looks new again today, and I only find out in Anki that I now have two cards for it. The professor asked in the first review (issue #1): what would this tool know about someone who has used it for a month? Today, nothing.

Matching words is also weak. The stem rules of the first design cannot join irregular forms (`ran` and `run`, `went` and `go`, `children` and `child`), and they wrongly join `hoped` with `hop`. Remembering cards across weeks makes this matter more, because the same word comes back in many different forms.

## What Changes

- The app keeps a history of the cards I have made, in a file in my own user folder (not in the program, not in git). A card is added to it when the deck it is in is downloaded.
- When I pick a word or term that already has a card in the history, the app does not make a new card straight away. It shows the earlier card (its sentence, its back and the date) and lets me **Skip** or **Make it anyway**. A card made anyway carries a "made before" note in the preview.
- In the reading app and its history, two words are the same when their base forms match (lemmas, from the `simplemma` package): `ran` matches `run`, `hoped` no longer matches `hop`.
- The back of a word card shows the base form in brackets when it differs from the word: `sighed (sigh)`.
- If the history cannot be read, the page says so and the app works on without it.
- New dependency: `simplemma==2.0.0`.

Not in this change: reading old `.apkg` decks into the history (may come next); reading the Anki collection itself (AnkiConnect); AI meanings; uploading documents. The first design's command-line tool is not changed: it keeps its stem rules, so the Homework 4 numbers stay reproducible.

## Capabilities

### New Capabilities
- `card-history`: the history of downloaded cards: where it is kept, what is in each entry, when entries are added, how an earlier card is found, and what happens when the file cannot be read.

### Modified Capabilities
- `reading-app`: picking a word or term checks the history; words match by base form; the back of a word card shows the base form; the app now writes one file of its own, the history.

## Impact

- New code: `src/sentmine/history.py` (the history file), `src/sentmine/lemma.py` (base forms).
- Changed code: `reading.py` (matching, the earlier-card check, the back), `app.py` (the history on download, the earlier card in the state), `web/index.html` (the Skip / Make it anyway panel, the "made before" note).
- Tests: new tests for the history and base forms. Existing tests that expected the back of a word card to be exactly the word change on purpose, for example `outliers` becomes `outliers (outlier)`.
- `pyproject.toml`: adds `simplemma==2.0.0`.

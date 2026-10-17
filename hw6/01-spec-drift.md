# Review 1: has the code drifted from the spec?

Session 6, slide 15. Looking for code the spec never described, and spec the code never built.

## How

- Counted the requirements in `openspec/specs/` (the durable spec) and in the open changes: `grep -c "^### Requirement"`.
- Counted the lines of code per module: `wc -l src/sentmine/*.py src/sentmine/web/index.html`.
- Read each requirement of the reading-app spec against `reading.py`, `app.py` and the page, and each function of those files against the spec.

## Found

| Part | Lines of code | Requirements in `openspec/specs/` |
|---|---|---|
| First design: command-line tool (`analyse.py`, `cli.py`, `deck.py`, `sentences.py`, `stem.py`, `words.py`) | 437 | 16 |
| Reading app (`reading.py`, `app.py`, `web/index.html`) | 656 | **0** |

1. **Far more code than spec.** The reading app, more than half of the code and the thing the README describes, has no requirement in the durable spec. Its 8 requirements exist only in the open change `add-reading-app`, which cannot be archived while its task 7.3 is open (trying Definition mode in a browser).
2. **A finished change left open.** `keep-quotes-whole` was complete (all tasks done) but not archived, so `openspec/specs/passage-analysis` still described the old sentence rule, which the code no longer follows.
3. **Two behaviours with no requirement at all.** The code refuses an edit that empties a side of a card (`Session.edit`), and cleans the deck name before it becomes a file name (`deck_file_name`). Both were logged as Claude's choices on 2026-10-09, but neither was in any spec.
4. **Spec the code never built:** none found. Every requirement of the reading-app spec has code and a test.

## Done

- Archived `keep-quotes-whole` (`openspec archive keep-quotes-whole --yes`). `openspec/specs/passage-analysis` now states that a sentence does not end inside an open quotation. `openspec validate --specs` passes 3 of 3.
- Added both behaviours from point 3 to the reading-app requirements in `add-reading-app`, each with a scenario.
- Not done: archiving `add-reading-app`. It waits for task 7.3, which needs a person to try Definition mode in the browser. Until then the durable spec does not describe the reading app. This is the largest open drift in the project.

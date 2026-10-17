# Review 2: names that aren't in the spec

Session 6, slide 16. Looking for named things, constants and behaviours that no spec, design or planning-log line asked for: decisions the agent made on its own that other code now depends on.

## How

- Listed every module-level constant, every `Timer`, `reconfigure`, note-type name and page-level text in `src/` with `grep`.
- Searched `PLANNING_LOG.md`, `openspec/specs/` and `openspec/changes/add-reading-app/` for each one.

## Found

| Name | Where | In a spec or the log? |
|---|---|---|
| `HOST`, `FIRST_PORT`, `LAST_PORT`, `DEFAULT_DECK_NAME`, `DEFAULT_MIN_LEN`, `EXIT_OK`, `EXIT_PROBLEM`, `ABBREVIATIONS` | `app.py`, `cli.py`, `sentences.py` | Yes, all of them |
| The page asking before a new text replaces the cards (`confirm(...)`) | `index.html` | Yes, log and design |
| A delay of **0.8 seconds** before the browser opens | `app.py`, `serve()` | **No.** A bare number with no explanation |
| `_tolerate_any_character`: a character the console cannot show is printed as `?` instead of crashing | `cli.py` | **No.** Added in the first build, never logged |
| The Anki note type is called **"sentmine: word in its sentence"**, its card template **"Word in sentence"** | `deck.py`, `MODEL` | Named in the first build for word cards; **definition cards now use the same note type**, so in Anki a term and its definition appear under a name that says "word in its sentence" |

Nothing was found on the scale of the slide's `apply_slack_buffer`: no extra feature the agent invented that the reader never asked for.

## Done

- The 0.8 seconds is now a named constant, `BROWSER_DELAY_SECONDS`, with a comment saying why it exists and that it was guessed, not measured.
- `_tolerate_any_character` and the note-type name are now in the planning log as Claude's past decisions.
- Not done: renaming the note type. Anki identifies a note type by its id and keeps the name it already has, so renaming would not reach decks already imported and could leave two note types in the reader's collection. It is listed as a later change, to decide with the reader.

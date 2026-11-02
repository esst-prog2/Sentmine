## Context

The session holds cards in memory; the preview shows and edits them; the download writes the deck and the card memory. The model was chosen by the spike in `spike/meanings/` (planning log, 2026-11-02). Key and design decisions are logged on the same date.

## Goals / Non-Goals

**Goals:** one button, one request, a result the reader can see and change; tests that never touch the network; an app that works without a key.

**Non-Goals:** automatic meanings; definition cards; a choice of model in the page.

## Decisions

**`meaning.py` holds everything about the model.** `suggest_meaning(word, sentence, key, post=...)` builds the request with the spike's prompt and returns the text. `post` is the function that does the HTTP call: the real one uses `urllib`, and tests pass a fake with an answer invented by hand, as in session 6's unit tests with constants. The real API is checked once by hand, as the integration test.

**No SDK.** One POST does not need a new package; the spike already showed it works with `urllib`.

**The session knows nothing about OpenAI.** `Session.suggest(card_id, ask)` takes any function from `(word, sentence)` to text. `create_app(session, ask=None)` passes it on; `serve()` builds the real one if a key exists. No `ask` means no button: the state carries `can_suggest`.

**Back format.** The back is `word_back`, a line break, then the meaning. The card keeps `heading`, its first line, so pressing again replaces the meaning instead of stacking them. It also means a press replaces any hand edit of the back, which is what pressing it asks for.

**No database change.** The back is already stored and searched, so meanings reach My cards without a new column. A separate column is only needed if meanings must be treated apart from the back.

**The key in the user folder.** The project folder is in OneDrive, so `.env` there is uploaded; and the Desktop shortcut does not start in that folder. `find_api_key()` reads the variable, then `.env` in `default_folder()`. It returns the key to `serve()`, which keeps it in the closure: it never reaches the state or the page.

## Risks / Trade-offs

- [A wrong meaning gets memorised] -> Shown in the preview first; the spike found 1 wrong in 20. The wrong one, `signed`, came from a sentence about the word itself, which gives no context.
- [A long quote is sent as the sentence] -> Costs a few more tokens; the sentence is what the card shows.
- [The model's name or price changes] -> One constant, `MODEL`; a failure says so in plain words.
- [A slow answer] -> The button shows it is waiting; the request times out after 30 seconds.

## Context

`Session.export` writes the preview's cards with `deck.write_notes` and then adds them to the memory. AnkiConnect listens on `http://127.0.0.1:8765` while Anki is open and takes JSON requests of the form `{"action": ..., "version": 6, "params": ...}`, answering `{"result": ..., "error": ...}`.

## Goals / Non-Goals

**Goals:** one button from preview to Anki; the same cards as Download; clear messages when Anki is not there.

**Non-Goals:** syncing both ways; editing notes already in Anki; replacing Download.

## Decisions

**`anki.py` takes the request function as a parameter,** as `meaning.py` does. Tests pass a fake AnkiConnect and never need Anki; the real one uses `urllib` with a short timeout.

**The order of requests.**
1. `version`: AnkiConnect must answer at least 6.
2. `modelNames`, then `createModel` only if the sentmine note type is missing, with the fields, template and name of `deck.MODEL`.
3. `createDeck`, which does nothing if the deck exists.
4. `canAddNotesWithErrorDetail` to find the cards already in the deck.
5. `addNotes` for the rest.

Asking first means one card already in Anki does not stop the others.

**Duplicates are Anki's rule:** the same front in the same deck and note type (`duplicateScope: "deck"`). That is how AnkiConnect checks, and it matches what a reader would call "already there".

**The same deck name as Download.** The name is cleaned by the same rule as the file name, without `.apkg`, so Download and Send put a deck called `new` in the same place.

**Remembering is shared with Download.** `Session.export` is split: writing the file, and `remember()`, which both Download and Send call after they succeed. Cards found already in Anki are remembered too, since the reader has them.

**Nothing leaves the computer.** The request goes to `127.0.0.1` only.

## Risks / Trade-offs

- [An old AnkiConnect without `canAddNotesWithErrorDetail`] -> The message asks the reader to update the add-on.
- [The reader renamed or changed the sentmine note type in Anki] -> Its name is still used; if its fields are no longer Front and Back, Anki refuses and the message shows Anki's reason.
- [Anki shows a window asking to allow the connection on first use] -> AnkiConnect does not ask for requests from the same computer; if it ever does, the reader allows it once.

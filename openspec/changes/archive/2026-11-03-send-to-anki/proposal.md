## Why

To get cards into Anki today I press Download, find the `.apkg` file, open it, and wait for Anki's import window. The speed test in Homework 5 counted that as part of the app's cost. AnkiConnect, a common Anki add-on, lets a program on the same computer add notes to the open Anki directly. Sending the cards with one button removes the file step, and the time can be measured before and after.

## What Changes

- A new button, Send to Anki, next to Download. It adds the cards, exactly as the preview shows them, to the deck named in the deck-name box, in the Anki that is open on this computer.
- The deck is made if it does not exist. The note type is the same one the `.apkg` uses, made in Anki if it is missing, so cards sent and cards downloaded look the same.
- A card whose front is already in that deck is not added again. The message says how many were added and how many were already there.
- Sent cards are remembered in My cards, as downloaded cards are.
- If Anki is not open or AnkiConnect is not installed, a message says so, and Download still works.
- Download stays as it is.

Not in this change: changing or deleting notes in Anki afterwards; reading cards back from Anki; tags; media.

## Capabilities

### New Capabilities
- `send-to-anki`: sending the cards to the open Anki through AnkiConnect, duplicates, and what happens when Anki cannot be reached.

### Modified Capabilities

None. Download and the history rules are unchanged; sending adds to the history by the same rule.

## Impact

- New: `src/sentmine/anki.py`; a route `POST /api/send`; a Send to Anki button in `web/index.html`; tests with a fake AnkiConnect.
- No new dependency: requests use `urllib`, to `127.0.0.1` only.
- The reader needs the AnkiConnect add-on (code 2055492159) to use the button.

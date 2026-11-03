## 1. Talking to AnkiConnect

- [x] 1.1 Write `anki.send_notes(notes, deck, post)` with the request order of the design; verify with a fake AnkiConnect: three cards added, the note type made when missing, one duplicate skipped, and each failure said in plain words

## 2. The session and the app

- [x] 2.1 Split `Session.export` into writing the file and `remember()`; add `Session.send(...)`; verify that Download's tests still pass and that sent cards are remembered while a failed send remembers nothing
- [x] 2.2 `POST /api/send` with the deck name; verify with the test client and a fake AnkiConnect
- [x] 2.3 A Send to Anki button, busy while sending; verify the script passes `node --check` and a screenshot

## 3. Wrap-up

- [x] 3.1 Run the whole suite and `openspec validate send-to-anki --strict`
- [x] 3.2 Send cards to the reader's real Anki: a new deck, then the same cards again (needs the reader)
- [x] 3.3 Measure with the reader: time from "cards ready" to "cards in Anki" for 10 cards, by Download and import, then by Send to Anki; log both

  Done by the reader on 2026-11-04 with 10 word cards from 2 sentences, timed by hand from "cards ready" to "cards in Anki": Download and import 30 s, Send to Anki 5 s.

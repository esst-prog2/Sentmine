## Why

Underlining shows the reader, in one text, which words they already have cards for. It does not show what happens over weeks: whether a card's word keeps coming back in what they read. A count of the texts in which each card was met again makes that visible on My cards. A card met in many texts is one that reading reviews by itself; a card never met again is one that only Anki reviews. It is also a number for the talk that comes from the reader's own reading.

## What Changes

- When the reader reads a text or opens a file, every remembered card whose word or term is in it is recorded as met in that text, once per text and card. Reading the same text again records nothing new.
- The text a card was made from does not count as meeting it again.
- My cards shows, for each card met again, how many texts it was met in and the day it was last met: `Met again in 3 texts, last on 2026-11-14`.
- The card shown when pointing at an underlined word says the same.
- The card memory gets a second table, so its layout goes from 2 to 3. An older sentmine refuses to open a memory of layout 3, as it does today for any newer layout.
- Deleting the last card for a word or term also deletes its meetings.

Not in this change: counting each place the word appears; meetings in Anki reviews (reading Anki results back is a later change).

## Capabilities

### New Capabilities
- `met-again`: when a card counts as met again, how it is kept, and where it is shown.

### Modified Capabilities

None. The memory, My cards and the underlining keep their rules; this adds to them.

## Impact

- `memory.py`: layout 3 with a `meetings` table; record meetings, mark the text a card was made from, count meetings per card, remove them with the last card.
- `reading.py`: an id for the text read (a hash of its words), passed when cards are remembered.
- `app.py`: record meetings after reading; the counts in My cards and in the cards shown when pointing.
- `web/cards.html` and `web/index.html`: the line `Met again in N texts, last on DATE`.

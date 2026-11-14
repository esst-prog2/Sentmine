## Why

sentmine remembers every card in its database, but the reader only meets that memory when they click a word again and are told it already has a card. While reading a new text they cannot see which words they have already learned. Showing them turns each new text into a quiet review: the reader meets their own card words in a new context and can check whether they still remember them. The professor named this direction first in his answer to Homework 7, because it builds on the card database and stays inside reading → remembering.

## What Changes

- When a text or PDF is read, every word that already has a word card in the memory is underlined with a dotted line, on pasted text and on a PDF's pages. Two words are the same by their base form, as for the earlier-card check (`ran` and `run`).
- Pointing at an underlined word shows that card: its front, its back and the day it was made.
- The message after reading says how many of the reader's card words are in the text.
- Clicking an underlined word does what it does today: the page shows the earlier card and offers Skip or Make it anyway.
- After cards are sent to Anki or downloaded, their words are underlined too, without reading the text again.

Not in this change: underlining definition terms (several words, matched differently); a review or quiz; reading results back from Anki.

## Capabilities

### New Capabilities
- `known-words`: which words of a text already have cards, how they are marked, and what pointing at one shows.

### Modified Capabilities

None. The earlier-card check and the memory keep their rules.

## Impact

- `memory.py`: the latest word card for each base form.
- `reading.py`: a word piece says which remembered card it matches; `lemma.base_form` is cached, since a book has tens of thousands of words.
- `app.py`: the cards for the words in the text, and the count in the message after reading.
- `web/index.html`: the underline on text and on PDF boxes, and the card shown when pointing.

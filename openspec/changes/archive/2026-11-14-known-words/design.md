## Context

The memory (`memory.py`) stores each sent or downloaded card as an `Entry` with a kind and a key; a word card's key is the base form of its word (`lemma.base_form`). `Session.layout()` sends the text to the page as pieces, and the page draws each word piece as a `.w` span, on text or as a box on a PDF's page. Picked words are marked from the `picked` flag of their piece.

## Decisions

**A word piece names its card by base form; the cards come once.** A remembered word may appear hundreds of times in a book, so a piece carries only `known: <base form>`, and the state carries `known_cards`: one card per base form that appears in the text (front and back as HTML, made the same way as My cards shows them, and the date). The page draws the card from there when the reader points at a word.

**One query per answer.** `CardMemory.word_cards()` returns the latest word card for each base form in one query. The memory holds hundreds of cards, not millions, so asking on every answer keeps underlines right after Send or Download without a cache that could go stale.

**`base_form` is cached.** The layout is built on every answer, and a 166-page book has about 55 000 words; `functools.lru_cache` on `base_form` (a pure function of the word) makes later answers fast.

**Underline, not colour.** A dotted underline in the accent colour is visible on text and on a PDF's page picture, does not hide the printed word, and stays distinct from the yellow of picked words and the blue of a drag.

**The card shows on pointing, in one box.** One floating box is placed under the word and filled from `known_cards`; it does not take the mouse, so clicks and drags go to the word as before.

## Risks / Trade-offs

- [Many underlines on a page for a reader with many cards] -> Only word cards count, and a reader makes cards for words they did not know; if it becomes noisy, a later change can limit it.
- [A base form shared by different words, such as `leaves` and `leave`] -> The same rule as the earlier-card check; the card shown lets the reader see which word it was.

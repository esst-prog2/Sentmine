## Why

On a real Guardian article, the card for a word inside quoted speech showed one sentence of the quote with a quotation mark that opened nowhere: `But he definitely needs to proceed with caution because we don't want to restoke division".` The quote was two sentences long and the splitter cut it at the full stop inside it. The reader decided that such a card should show the whole quote, with the words that introduce it.

This was found through Homework 5. Its first test took its expected sentences from what the app had already shown, so it could not catch this. The repair fixed the expected wording first, from the article text, and the test was red before the program changed.

## What Changes

- A sentence no longer ends inside an open quotation. Quoted speech of several sentences stays one sentence, together with the words before the opening mark (`One cabinet minister told the Guardian: "..."`).
- Pairs counted: curly double quotation marks, guillemets, and straight double quotation marks. Single quotation marks are not counted, because the closing one is also the apostrophe.
- A quotation that is never closed runs to the end of its paragraph and no further.

Not in this change: cutting a long quote down to the sentence with the word in it (the reader can shorten a card in the preview); single quotation marks; quotes that continue over several paragraphs.

## Capabilities

### New Capabilities

None.

### Modified Capabilities
- `passage-analysis`: the sentence-splitting requirement gains the rule that a sentence does not end inside an open quotation.

## Impact

- `src/sentmine/sentences.py`: one new check in `split_sentences`.
- Every card made from quoted speech becomes longer, in the reading app and in the first design's command-line tool. The number of cards does not change: the spike's 103 cards from the Guardian article are still 103.
- The number of sentences counted in a text with quotes goes down.
- `tests/test_real_article.py` has new expected wording for two of its four cards; `tests/test_quoted_speech.py` is new.

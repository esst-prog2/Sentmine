## Why

The back of a word card holds only the word, so to study it I still have to look the meaning up, away from the sentence I read. A dictionary gives every meaning of a word; a small language model that sees the sentence can give the one that fits. The professor suggested exactly this: a small, cheap model for definitions.

The spike in `spike/meanings/` chose the model. Judged blind by the reader on 20 words from real texts, `gpt-5-nano` and `gpt-5-mini` each got 19 of 20 right, above the bar of 18 set beforehand, and the rule picks the cheaper: `gpt-5-nano`, $0.00028 for the 20 words.

## What Changes

- Each word card in the preview gets a **Suggest meaning** button. It sends the word and its sentence to the model and puts a short English explanation on the back, under the word. Pressing it again replaces the explanation.
- The reader can edit or remove the meaning in the preview, as with any card. It is downloaded and remembered with the card.
- Without an API key the button is not shown, and everything else works as before.
- If the request fails (no network, no credit, a refused key) the card stays as it was and the page says why.
- The key is read from the variable `OPENAI_API_KEY` or from `.env` in the reader's user folder.

Not in this change: definition cards (their back is the passage the reader marked); suggesting meanings automatically for every card; translation; choosing the model in the page; correcting the base form from the sentence.

## Capabilities

### New Capabilities
- `ai-meanings`: the button, what is sent, where the meaning goes, the key, and what happens on failure.

### Modified Capabilities
- `reading-app`: the app may now send one word and its sentence to the model when the reader asks; nothing else leaves the computer.

## Impact

- New: `src/sentmine/meaning.py`; a `Suggest meaning` button in `web/index.html`; a route in `app.py`.
- No new package (Python's `urllib`), no change to the database layout (the back is already stored).
- A cost per press, measured at about $0.000014. The first design's command-line tool is not touched.

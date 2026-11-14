## Why

Sending a whole web page to sentmine brings its clutter, and guessing sentences on a web page goes wrong often (links, boxes and line breaks cut them). The reader wants to choose on the real page instead: select a sentence or a definition, right-click once, and make the card in a panel beside the page (decided 2026-11-14).

## What Changes

- The extension adds two right-click items on selected text: "Word card from this sentence" and "Definition card from this". Either one opens a side panel beside the page and sends the selection to sentmine as a clip.
- sentmine keeps clips apart from the text in Read: a second reading session at `/clip`, where each new clip is added after the earlier ones and their cards stay until they are sent or downloaded. Reading a PDF in Read is never touched by a clip.
- The side panel shows sentmine's own page for the clips, narrow: click a word for a word card, as in Read; in a definition clip, one drag over the term makes the definition card, the clip being its definition. Download, Send to Anki, edit, cloze and Suggest meaning work as in Read.
- The browser hands the extension the selected text itself, so the right-click needs no access to the page.

## Capabilities

### New Capabilities
- `clip-panel`: making cards from text selected on a web page, in a side panel beside it.

### Modified Capabilities

None.

## Impact

- `reading.py`: a session can add a clip after the earlier ones, keeping their cards.
- `app.py`: the reading routes also answer under `/clip`, for the clip session; `/clip` serves the page.
- `web/index.html`: the same page in clip mode (narrow, no paste box, the definition shortcut).
- `extension/`: the two menu items (background worker), the side panel; permissions `contextMenus` and `sidePanel`.

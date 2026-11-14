## Why

The reader reads PDFs and web pages in the browser (Canvas files among them), but sentmine can only read what is pasted or chosen with Open a file, so every text means saving or copying it first. The reader asked for the browser extension now, in a small first version (2026-11-14), although the professor placed it after the December demos.

## What Changes

- A browser extension for Edge and Chrome (in `extension/`, loaded unpacked): one toolbar button, "Open in sentmine".
- On a PDF open in a tab, the button sends the PDF to sentmine; on a web page, it sends the page's text (the selected text if there is any, otherwise the page's main text). Then it shows sentmine's Read page, in a tab already open or a new one.
- The extension finds sentmine on ports 8000 to 8010 by asking each port who it is; a new `/api/hello` answers. When sentmine is not running, the button says so and how to start it.
- The extension asks only for the tab the reader clicked on (`activeTab`) and for sentmine's own address; it reads nothing until the button is pressed, and sends nothing anywhere but sentmine on this computer.
- sentmine now refuses requests that change something when they come from another website (any `Origin` that is not its own page or a browser extension). Until now any page the reader visited could send sentmine a file.

## Capabilities

### New Capabilities
- `open-in-sentmine`: opening the page or PDF in the browser's current tab in sentmine's reader.

### Modified Capabilities

None.

## Impact

- `extension/`: manifest, service worker, the logic in a module that node can test.
- `app.py`: `/api/hello`; the origin check before every request that changes something.
- Not in this version: picking words on web pages, PDFs that need a login to download again (a Canvas file page: the reader opens the PDF itself in a tab first), local files (Open a file does that).

## 1. The app

- [x] 1.1 `GET /api/hello`; refuse changing requests from other origins with 403; tests with the test client (other site refused, own page and extension accepted, no Origin accepted)

## 2. The extension

- [x] 2.1 Manifest V3 (activeTab, scripting, sentmine's address only), a small panel that opens when the button is pressed (no background worker), the logic in a module testable with node
- [x] 2.2 Find sentmine on 8000-8010 by `/api/hello`; send a PDF as a file or a page's text; show the Read page; clear messages for every case it cannot do
- [x] 2.3 Node tests for choosing what to send and for finding the port

## 3. Check and wrap-up

- [x] 3.1 In headless Edge with the extension loaded: a web page and a PDF end up in sentmine's Read page; a page of another site changes nothing (Edge itself blocks it before it reaches the app; the app's 403 is covered by the app's tests)
- [x] 3.2 How to install it, in the README; the whole suite; `openspec validate open-in-sentmine --strict`
- [ ] 3.3 The reader loads it in Edge and opens a page and a PDF with it (needs the reader)

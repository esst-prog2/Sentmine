## 1. The picture

- [x] 1.1 Draw a box of a PDF page as a PNG (pages.py); a test with a generated PDF
- [x] 1.2 Cards hold pictures; back_html and the note include them; cloze puts them in the second field; tests

## 2. To Anki

- [x] 2.1 Notes carry media; the deck file contains them; Send to Anki stores them first (storeMediaFile); tests with the fake Anki

## 3. The app and the page

- [x] 3.1 Routes to add and remove a picture and to serve it; tests
- [x] 3.2 Add a picture: draw a box on the page, Esc cancels; the picture on the card with a remove button
- [x] 3.3 Headless Edge: add a picture to a card on the course PDF; the deck file contains it

## 4. Web pages and picture only

- [x] 4.1 The app takes a PNG for a card, at most 5 MB; tests
- [x] 4.2 The extension: right-click an image, to the chosen card; the panel shows it
- [x] 4.3 Headless Edge on a Wikipedia page; the deck holds the pictures

- [x] 4.4 Paste a picture (Ctrl+V) onto the card being edited or the chosen card; the editor keeps what is typed; headless Edge
- [x] 4.5 The back as a small document: pictures inline where the reader puts them ([[picture:name]] in the text), Delete removes one, Edit chooses the card, Cut from the PDF page inside the editor; the picture buttons removed; a web picture shows in the open editor; tests and headless Edge

## 5. Wrap-up

- [x] 5.1 README, the whole suite, `openspec validate card-pictures --strict`
- [ ] 5.2 The reader tries it on a formula and a graph (needs the reader)

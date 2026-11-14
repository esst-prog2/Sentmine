## 1. The app

- [x] 1.1 A session adds a clip after the earlier ones, keeping cards; a definition clip is one paragraph; tests
- [x] 1.2 The reading routes also under `/clip` for the clip session, `/clip` serves the page; Read untouched by clips; tests

## 2. The page in clip mode

- [x] 2.1 Calls go to `/clip/api` in clip mode; narrow layout, no paste box, newest clip in view
- [x] 2.2 In a definition clip, one drag over the term makes the card

## 3. The extension

- [x] 3.1 Background worker with the two menu items; opens the side panel, sends the clip, tells the panel
- [x] 3.2 The side panel: finds sentmine, shows `/clip`, reloads on a new clip, says when sentmine is not running

## 4. Check and wrap-up

- [x] 4.1 Headless Edge: a word clip and a definition clip make their cards in the clip page at panel width; Read untouched
- [x] 4.2 README, the whole suite, `openspec validate clip-panel --strict`
- [ ] 4.3 The reader tries it on a web page (needs the reader)

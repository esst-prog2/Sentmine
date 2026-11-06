## 1. The demo

- [x] 1.1 Take the cards from the app on the reader's PDF: the word card from page 13, the cloze card from page 5, the page numbers from `pages.locate`
- [x] 1.2 Ask the model once for the meaning of `simultaneously` in its sentence, with the reader's key, and quote the answer as the model's
- [x] 1.3 Check every quoted message against `app.py` and every claim about My cards against the code
- [x] 1.4 Rewrite the opening lines and section 1 of the README

## 2. Checks

- [x] 2.1 `tests/test_readme_demo.py`: the demo's sentences pasted into the app give the cards and messages the README shows; verify it fails when the README is changed (3 failed) and passes again
- [x] 2.2 Run the whole suite and `openspec validate readme-demo --strict`

## 3. Hand-in

- [ ] 3.1 The reader reads section 1 and agrees it is their demo (needs the reader)
- [ ] 3.2 Commit, push, open the pull request; paste section 1 on Canvas (needs the reader)

## 1. One shape of card

- [x] 1.1 The word card's front and back swapped (word, then its sentence); the term in bold in every passage; cloze for every card, off at first; tests
- [x] 1.2 Cards remembered in the earlier shape shown as they were (`old_layout`); tests
- [x] 1.3 Suggest meaning under the passage, replacing its own earlier meaning; tests

## 2. Whole sentences and one right-click

- [x] 2.1 `whole_sentences` for a selection with the text around it; Read's definition drag snapped to the text's sentences; tests
- [x] 2.2 `Session.add_clip` and `/clip/api/text`: one word or a bold term makes the card at once; tests
- [x] 2.3 The extension: one menu item; the paragraph around the selection and a bold phrase read at the right-click, without a page's style or a formula's source; node tests
- [x] 2.4 The page: one label, cloze on every card, one kind of clip

## 3. The words that show the meaning

- [x] 3.1 The prompt asks for the key on a second line; only a short part really in the sentence is kept; the card underlines it, also in Anki; tests with written answers
- [x] 3.2 Tried on the real model: the first wording often gave the whole sentence (3 of 9 kept); with "never the whole sentence", 4 of 6 kept

## 4. Checks and wrap-up

- [x] 4.1 Headless Edge on Wikipedia's Poisson distribution: a word, a bold term, a rough selection; the earlier clip, editor, paste, picture, keyboard, gesture and place checks again
- [x] 4.2 README, the promo page's extension section, `openspec validate one-card --strict`
- [ ] 4.3 The reader tries it for a week of reading (needs the reader)

## 5. Pictures where the cursor was; a drag makes its card; Add sentences

- [x] 5.1 A picture cut from the PDF or sent from a web page goes where the cursor last was, Term or Passage; Esc leaves no mark; the editor check
- [x] 5.2 A drag (or keyboard marking) over a term of up to 8 words makes its card at once with its sentence; a longer drag says what to do; tests and the gesture and keyboard checks
- [x] 5.3 Add sentences: the card keeps its sentence numbers; a click adds or takes out a sentence, lit in the text; an edited passage keeps what was typed; clip numbers move when a clip is removed; tests and the gesture check

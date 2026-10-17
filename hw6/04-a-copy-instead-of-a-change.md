# Review 4: a copy instead of a change

Session 6, slide 18. Looking for units that do almost the same job under different names, because the agent built a thing again instead of finding what was there.

## How

- Listed every regular expression and helper in `src/` and compared them (`grep -n -E "re.compile|^def " src/sentmine/*.py`).
- Compared the helpers at the top of each test file.
- Compared the two card types, `analyse.Card` and `reading.Flashcard`.

## Found

1. **Paragraph splitting, written twice.** `reading.py` had its own `_PARAGRAPH_BREAK` and `_LINE_BREAK`, character for character the same as in `sentences.py`, and its own copy of the loop that splits a text at blank lines and joins wrapped lines. Built when the reading app was added, instead of reusing the splitter's.
2. **The same regular expression twice in one file.** `reading.py` defined `_NEWLINES` and `_LINE_BREAK` with the same pattern, `\s*\n\s*`.
3. **"1 card / 2 cards", written twice.** `cli._count(number, noun)` for the command-line summary and `app.count_text(number)` for the page header.
4. **A test helper, written three times.** `place_of` in `test_reading.py`, `click` in `test_real_article.py` and `word_place` in `test_app.py` each walked the page layout to find a clickable word, in slightly different ways.
5. **Two card types.** `analyse.Card` (word and sentence, for the first design) and `reading.Flashcard` (any front and back, editable, for the app). Not a copy: they hold different things for different parts of the program.

## Done

- `sentences.py` now has one `paragraphs(text)` function. `split_sentences` and `reading.tidy` both use it, and the copied expressions are gone from `reading.py`, including the duplicate `_NEWLINES`/`_LINE_BREAK` pair.
- One `plural(number, noun)` in `words.py`, used by the command-line summary and the page header.
- One test helper, `tests/reading_helper.py`, used by all three test files.
- The two card types stay, for the reason in point 5.
- All 306 tests pass before and after, unchanged in what they check.

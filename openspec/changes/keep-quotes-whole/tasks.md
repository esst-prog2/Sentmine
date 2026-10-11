## 1. Expected value first

- [x] 1.1 Log the exact expected wording of the `restoke` and `constituents` cards, copied from `spike/article.txt`, before any test or code change; verify it is committed on its own
- [x] 1.2 Put that wording into `tests/test_real_article.py` and run it against the unchanged program; verify 2 of the 5 checks fail and keep the output in `hw5/red_run_quotes.txt`

## 2. The fix

- [x] 2.1 In `split_sentences`, do not end a sentence while a quotation is open (curly double marks, guillemets, straight double marks; not single marks; per paragraph); verify `tests/test_real_article.py` passes and keep the output in `hw5/green_run_quotes.txt`
- [x] 2.2 Add tests for each new scenario of the sentence-splitting requirement in `tests/test_quoted_speech.py`; verify they pass

## 3. Nothing else moved

- [x] 3.1 Run the whole test suite; verify every earlier test passes unchanged
- [x] 3.2 Run the first design's tool on the spike article with `spike/known_real_irregular.txt`; verify it still writes 103 cards
- [x] 3.3 Change line 6 of `src/sentmine/sentences.py` as `hw5/break_the_promise.py` does; verify the Homework 5 test still goes red, then put the line back

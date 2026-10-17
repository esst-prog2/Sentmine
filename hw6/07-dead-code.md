# Review 7: dead code

Session 6, slide 20, right column. Looking for functions the agent wrote that nothing calls, and features built twice under different names.

## How

- For every function, class and constant in `src/sentmine/*.py`, counted its uses outside its own definition, separately in `src/` and in `tests/` (`grep -rw`).
- For every function in the page script, counted its uses in `index.html`.
- Features built twice were covered by review 4.

## Found

| Name | Uses in the program | Uses in tests | Verdict |
|---|---|---|---|
| `analyse.parse_known(text)` | **0** | 4 | Dead. The command-line tool splits the known-words file itself and calls `known_stems` directly, so this was only ever called by its own tests |
| `Analysis.new_words` | **0** | 0 | Dead. A property returning `len(cards)`, never read |
| every other function in `src/` | at least 1 | | Used |
| `element`, `say`, `call`, `draw`, `drawText`, `drawCard`, `setMode` in the page | 2 to 19 each | | Used |

The spike and Homework 5 scripts (`spike/*.py`, `hw5/*.py`) are not called by the program on purpose: they are the evidence the professor reruns, so they are not dead code.

## Done

- Removed `parse_known` and `new_words`.
- The four tests of `parse_known` checked something the program really does (blank lines, Windows line endings, an empty file and a number in the known-words file are all handled). They now test `known_stems` on the lines of the text, which is the path the command-line tool actually takes, so that behaviour stays covered.
- 307 tests pass.

# Review 5: errors that disappear

Session 6, slide 19. Looking for `except Exception`, `except: pass`, `return None` after an error, and their JavaScript twins: places where the program carries on as if nothing happened.

## How

`grep -n -E "except|catch|\bpass\b|return None" src/sentmine/*.py src/sentmine/web/index.html spike/*.py hw5/*.py`, then read every hit.

## Found

| Where | What it does | Verdict |
|---|---|---|
| `cli._min_len` | `except ValueError` → an argparse error naming the value | Fine: the error is reported |
| `cli._read_text` | `except UnicodeDecodeError` / `OSError` → `InputProblem` with a message, exit 2 | Fine |
| `cli.main` | `except InputProblem`, `except OSError` → message, exit 2 | Fine |
| `cli._tolerate_any_character` | `except (AttributeError, ValueError): pass` | Fine: some output streams cannot be reconfigured (under pytest, for example); nothing is lost |
| `app.free_port` | `except OSError: continue` | Fine: a port in use means "try the next one", by design |
| `reading._card_with_key` | `return None` | Fine: means "no such card", not an error |
| **`cli._same_file`** | `except OSError: return False` | **Error that disappears.** If the paths could not be resolved, the check answered "not the same file", and the deck could then overwrite the passage or the known-words file, which the spec says must never happen |
| **page script, `call()`** | one `try` around both the request and reading its JSON | **Error with the wrong name.** If the app failed inside (a bug gives an HTML error page, not JSON), the page said "The app is not answering. Is sentmine still running?", sending the reader to look for a closed terminal instead of an error |
| page script, download | `response.json().catch(() => ({}))`, then "The deck could not be made." | Fine: the reader still sees that it failed |

No `except Exception` and no `except: pass` anywhere in the program or the spike scripts.

## Done

- `_same_file` now compares the paths as written when they cannot be resolved, instead of assuming they differ. New test `test_input_file_is_protected_even_when_paths_cannot_be_resolved`: it fails on the old code and passes on the new.
- The page now tells the two failures apart: "The app is not answering" only when no answer came back; "The app ran into an error (500). The terminal running sentmine shows what happened." when the app answered with an error.
- 307 tests pass. The page script passes `node --check`; the new message has not been seen in a browser.

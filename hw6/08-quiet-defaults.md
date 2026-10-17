# Review 8: the quiet default

Session 6, slide 21. Looking for `.get(key, default)` where a missing key is really a bug, and defaults that change behaviour instead of signalling a problem.

## How

- `grep -n -E "\.get\(| or \{\}| or \"| \|\| " src/sentmine/*.py src/sentmine/web/index.html` for fallbacks.
- `grep -n -E "def [a-z_]+\(.*=" src/sentmine/*.py` for every default value in a function signature.
- Each default checked against the spec and the planning log: chosen, or nobody's decision?

## Found

| Default | Where | Verdict |
|---|---|---|
| Deck name `new` when none is given (`request.args.get("name", "")` → `deck_file_name`) | `app.py` | Chosen: the spec says `new` by default |
| `request.get_json(silent=True) or {}` | `app.py`, `sent()` | Not quiet: a request without usable JSON still gets a 400 with a message naming the missing field |
| `create_app(session=None)` makes a new session; `serve(open_browser=True)` | `app.py` | Chosen: the command opens the browser (spec); tests pass their own session |
| `Flashcard.word = ""`, `place = None` | `reading.py` | Mean "this is a definition card"; every reader of them checks for that |
| `message \|\| HINTS[mode]`, `data.error \|\| "Something went wrong."` | page script | Fallback text for the reader, never a silent decision |
| Download file name falls back to `new.apkg` if the header has no name | page script | The server always sends the name, so this only applies if the server breaks; harmless |
| **`min_len: int = 3`** in `analyse()` and **`DEFAULT_MIN_LEN = 3`** in `cli.py` | `analyse.py`, `cli.py` | **The same default, decided in two places.** The command-line tool always passes its own value, so `analyse()`'s `3` is used only when `analyse` is called without one (the tests). Change the documented default in `cli.py` and the function would quietly keep the old `3` for every other caller |

No `.get(key, default)` was found where a missing value should have been an error.

## Done

- `DEFAULT_MIN_LEN = 3` is now defined once, in `analyse.py`, with a comment pointing to the spec; `analyse()` uses it as its default and the command-line tool imports it for `--min-len` and its help text.
- `sentmine --help` still says "(default: 3)". 307 tests pass.

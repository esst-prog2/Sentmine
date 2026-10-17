# Review 6: dependencies nobody chose

Session 6, slide 20, left column. For each package: does it exist, is it used, is it pinned to one exact version?

## How

- `pyproject.toml` for what the project declares.
- `python -m pip index versions <package>` to check each name exists on PyPI, and `pip show` for its home page and what it pulls in.
- `grep -rl -E "^(import|from) <package>" src tests` to check each is used, and a list of every non-standard-library import in `src/` to check nothing is used without being declared.

## Found

| Package | Exists on PyPI | Used in | Chosen when | Pinned |
|---|---|---|---|---|
| `genanki` | Yes, 0.13.1, github.com/kerrickstaley/genanki | `deck.py` | MVP explore, by the user (log 2026-09-26) | **No** (`"genanki"`) |
| `flask` | Yes, 3.1.3 | `app.py` | Reading app, by Claude (log 2026-10-09) | **No** (`"flask"`) |
| `pytest` (tests only) | Yes, 9.1.1 | every test file | MVP design, by Claude | **No** (`"pytest"`) |

- No invented package names: all three exist and are the well-known projects of those names.
- No unused dependency, and nothing imported in `src/` that is not declared: the only third-party imports are `genanki` and `flask`.
- None was pinned. A fresh install could pull a newer version with different behaviour, which nobody would have chosen or tested.
- The packages they pull in (for example `frozendict` and `pyyaml` for genanki; `werkzeug` and `jinja2` for flask) are not pinned either. A file `uv.lock`, which would pin all of them, exists on this computer but was never committed: it was made by running `uv` once during Homework 4, not on purpose.

## Done

- Pinned all three in `pyproject.toml` to the versions the 307 tests pass with: `genanki==0.13.1`, `flask==3.1.3`, `pytest==9.1.1`. Reinstalled with `pip install -e ".[dev]"` and ran the suite again: 307 passed.
- Not done: pinning the packages they pull in. That needs a lock file made on purpose; the stray `uv.lock` was left uncommitted, since nobody checked what it contains.

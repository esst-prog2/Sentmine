"""Homework 5, step 5: change one line of the program so that the promise breaks.

The line is the one in src/sentmine/sentences.py that starts with `_END = re.compile`
and says which marks end a sentence. It was line 6 during Homework 5; the docstring
added in Homework 6 (review 3) moved it to line 16. This script finds it by its text,
not its number, and adds the comma to the marks, so a sentence is cut at its first
comma and a card no longer shows the whole sentence.
Undo it with:  git checkout -- src/sentmine/sentences.py
"""

import io
from pathlib import Path

PATH = Path(__file__).parent.parent / "src" / "sentmine" / "sentences.py"
WORKING = '_END = re.compile(r"[.!?]+['
BROKEN = '_END = re.compile(r"[.!?,]+['

text = io.open(PATH, encoding="utf-8", newline="").read()
if text.count(WORKING) != 1:
    raise SystemExit("the line to change was not found exactly once; nothing changed")
line = text[: text.index(WORKING)].count("\n") + 1
io.open(PATH, "w", encoding="utf-8", newline="").write(text.replace(WORKING, BROKEN))
print(f"changed line {line} of src/sentmine/sentences.py (`_END = re.compile`): the sentence-ending marks")
print("  were: [.!?]")
print("  now:  [.!?,]")

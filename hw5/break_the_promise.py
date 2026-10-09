"""Homework 5, step 5: change one line of the program so that the promise breaks.

The line is line 6 of src/sentmine/sentences.py, the one that says which marks
end a sentence. This script adds the comma to them, so a sentence is cut at its
first comma and a card no longer shows the whole sentence.
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
io.open(PATH, "w", encoding="utf-8", newline="").write(text.replace(WORKING, BROKEN))
print("changed line 6 of src/sentmine/sentences.py: the sentence-ending marks")
print("  were: [.!?]")
print("  now:  [.!?,]")

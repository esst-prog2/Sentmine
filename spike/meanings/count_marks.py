"""Spike: count the reader's marks in to_judge.txt per model. Run from the repository root."""

import json
import re
from collections import Counter
from pathlib import Path

FOLDER = Path("spike/meanings")
key = json.loads((FOLDER / "key.json").read_text(encoding="utf-8"))
marks = {}
for line in (FOLDER / "to_judge.txt").read_text(encoding="utf-8").splitlines():
    found = re.match(r"^\s*([A-Za-z_])\s+(\d+[ab]):", line)
    if found:
        marks[found.group(2)] = found.group(1).upper()
unmarked = [label for label in key if marks.get(label) not in ("R", "W")]
right, wrong = Counter(), []
for label, model in key.items():
    if marks.get(label) == "R":
        right[model] += 1
    elif marks.get(label) == "W":
        wrong.append((label, model))
print("answers found:", len(marks), "of", len(key), "| unmarked:", unmarked)
for model in sorted(set(key.values())):
    print(model, "right:", right[model], "of", sum(1 for m in key.values() if m == model))
print("wrong:", wrong)

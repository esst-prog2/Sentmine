"""Run sentmine on the article, then find how many known words bring the card count to 20.

Each card is one distinct word stem, so adding one card's word to known.txt removes
exactly one card. The count needed is therefore (cards now - 20); this script checks it
by actually re-running sentmine with that many card words added to known.txt.
"""
import re
import subprocess
from pathlib import Path

here = Path(__file__).parent
root = here.parent
article = here / "article.txt"
known = here / "known.txt"
known_plus = here / "known_plus_to_20.txt"
deck = here / "article.apkg"


def run(known_file):
    result = subprocess.run(
        ["uv", "run", "sentmine", str(article), "--known", str(known_file), "--deck", str(deck), "--force"],
        cwd=root, capture_output=True, text=True, encoding="utf-8", check=True,
    )
    return result.stdout


out = run(known)
print(out.strip())
match = re.search(r"Wrote (\d+) new cards.*?: (.*)\.$", out.strip(), flags=re.S)
cards = [w.strip() for w in match.group(2).split(",")]
needed = len(cards) - 20
print(f"cards now: {len(cards)}; words to add to known.txt to reach 20: {needed}")

extra = cards[:needed]
known_plus.write_text(known.read_text(encoding="utf-8") + "\n".join(extra) + "\n", encoding="utf-8")
check = run(known_plus)
print("check:", check.strip().splitlines()[-1][:120])

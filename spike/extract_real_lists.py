"""Build known_real_lists.txt from the four saved Pattern Based Writing pages.

Each list entry is a numbered lowercase line, e.g. `316. bet  2   +`. Capitalised numbered
lines are example sentences and are skipped.
"""
import html
import re
from pathlib import Path

here = Path(__file__).parent
pages = here / "real_lists"
words = set()

for name in ["verbs", "adjectives", "nouns", "adverbs"]:
    raw = (pages / f"{name}.html").read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"(?is)<(script|style|noscript|head)[^>]*>.*?</\1>", " ", raw)
    text = html.unescape(re.sub(r"<[^>]+>", "\n", raw))
    for line in text.splitlines():
        match = re.match(r"^\s*\d+\.\s+([a-z][a-z'\-]*)\b", line.strip())
        if match:
            words.add(match.group(1))

(here / "known_real_lists.txt").write_text("\n".join(sorted(words)) + "\n", encoding="utf-8")
print(len(words), "distinct words")

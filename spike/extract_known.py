"""Pull the headwords out of an Oxford word-list PDF into a known file, one per line.

usage: extract_known.py [PDF] [OUT]   (defaults: American_Oxford_3000.pdf -> known.txt)
"""
import re
import sys
from pathlib import Path

from pypdf import PdfReader

here = Path(__file__).parent
pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "American_Oxford_3000.pdf"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else here / "known.txt"
reader = PdfReader(str(pdf))
STOP_AT = {"definite", "indefinite", "article", "modal", "number", "exclam"}

words = set()
entries = 0
for page in reader.pages:
    for line in page.extract_text().splitlines():
        if not re.match(r"^[a-z]", line):
            continue
        entries += 1
        for token in line.split():
            if token.endswith(".") or re.fullmatch(r"[ABC][12]", token) or token in STOP_AT:
                break
            token = token.rstrip(",").lower()
            if re.fullmatch(r"[a-z'\-]+", token):
                words.add(token)

out.write_text("\n".join(sorted(words)) + "\n", encoding="utf-8")
print(entries, "entries,", len(words), "distinct headwords")

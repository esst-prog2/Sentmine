"""Pull the headwords out of the Oxford 3000 PDF into known.txt, one per line."""
import re
from pathlib import Path

from pypdf import PdfReader

here = Path(__file__).parent
reader = PdfReader(str(here / "American_Oxford_3000.pdf"))
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

(here / "known.txt").write_text("\n".join(sorted(words)) + "\n", encoding="utf-8")
print(entries, "entries,", len(words), "distinct headwords")

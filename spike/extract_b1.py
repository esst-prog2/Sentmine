"""Pull the headwords out of the Cambridge B1 Preliminary vocabulary list into b1_words.txt.

The list is two columns per page. Each headword line looks like `word (pos)`; example
sentences start with a bullet and are skipped. Multi-word headwords are split into words.
"""
import re
from pathlib import Path

import pdfplumber

here = Path(__file__).parent
HEADWORD = re.compile(r"^([A-Za-z][A-Za-z'\-/ ]*?)\s*\((adj|adv|n|v|det|prep|conj|pron|exclam|modal|number|art)\b[^)]*\)")

words = set()
with pdfplumber.open(str(here / "b1_preliminary_vocabulary.pdf")) as pdf:
    for page in pdf.pages:
        half = page.width / 2
        for box in [(0, 0, half, page.height), (half, 0, page.width, page.height)]:
            text = page.crop(box).extract_text(x_tolerance=1.5) or ""
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("•"):
                    continue
                match = HEADWORD.match(line)
                if not match:
                    continue
                for headword in match.group(1).split("/"):
                    for token in headword.split():
                        token = token.lower().strip("'-")
                        if re.fullmatch(r"[a-z][a-z'\-]*", token):
                            words.add(token)

(here / "b1_words.txt").write_text("\n".join(sorted(words)) + "\n", encoding="utf-8")
print(len(words), "distinct words")

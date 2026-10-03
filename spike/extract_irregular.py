"""Pull every form (infinitive, past simple, past participle) from the Cambridge irregular
verbs PDF into irregular_forms.txt, one word per line. Uses pdfplumber because pypdf
splits words at single glyphs in this PDF.
"""
import re
from pathlib import Path

import pdfplumber

here = Path(__file__).parent
SKIP = {"irregular", "verbs", "infinitive", "past", "simple", "participle"}

forms = set()
with pdfplumber.open(str(here / "irregular_verbs.pdf")) as pdf:
    for page in pdf.pages:
        for line in page.extract_text(x_tolerance=1.5).splitlines():
            for token in re.split(r"[\s/]+", line):
                token = token.lower()
                if re.fullmatch(r"[a-z]+", token) and token not in SKIP:
                    forms.add(token)

(here / "irregular_forms.txt").write_text("\n".join(sorted(forms)) + "\n", encoding="utf-8")
print(len(forms), "distinct forms")

"""Pull the article body paragraphs out of the saved Guardian HTML into article.txt."""
import html
import re
from pathlib import Path

here = Path(__file__).parent
raw = (here / "article_raw.html").read_text(encoding="utf-8", errors="replace")

MARKER = "Prefer the Guardian on Google"
JUNK = ("document.", "function", "addEventListener", "{", "}", "=>", "Search input")

paragraphs = []
for match in re.finditer(r"<p[^>]*>(.*?)</p>", raw, flags=re.S | re.I):
    text = re.sub(r"<[^>]+>", "", match.group(1))
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    if MARKER in text:
        text = text.split(MARKER, 1)[1].strip()
    if len(text) >= 60 and not any(j in text for j in JUNK):
        paragraphs.append(text)

FIXES = {"â€™": "'", "â€˜": "'", "â€œ": '"', "â€\u009d": '"', "â€": '"', "â€“": "–", "â€”": "—", "Ã©": "é"}
body = "\n\n".join(paragraphs) + "\n"
for bad, good in FIXES.items():
    body = body.replace(bad, good)
(here / "article.txt").write_text(body, encoding="utf-8")
print(len(paragraphs), "paragraphs,", sum(len(p.split()) for p in paragraphs), "words")

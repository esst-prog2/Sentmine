import re, html, sys
for k in ["verbs","adjectives","nouns","adverbs"]:
    raw = open(f"{k}.html", encoding="utf-8", errors="replace").read()
    raw = re.sub(r"(?is)<(script|style|noscript|head)[^>]*>.*?</\1>", " ", raw)
    text = html.unescape(re.sub(r"<[^>]+>", "\n", raw))
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    open(f"{k}.txt", "w", encoding="utf-8").write("\n".join(lines))
    print(k, len(lines), "lines")

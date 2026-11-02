"""Spike: the 20 words and the sentences they appear in, taken from the reader's real texts.

Run from the repository root: python spike/meanings/make_input.py
It writes spike/meanings/words.json. Sentences are found with sentmine's own splitter,
so each one is what the reading app would send to a model.
"""

import json
import re
from pathlib import Path

from sentmine.sentences import split_sentences

ARTICLE = Path("spike/article.txt").read_text(encoding="utf-8-sig")
SKEW = "Outliers can skew it considerably."  # the paragraph in README section 1

# The three cards in the reader's card memory on 2026-10-22, copied from cards.db.
FROM_CARDS = {
    "paraphrasing": "Paraphrasing is rewriting a passage, sentence, or thought in your own words while keeping the original meaning.",
    "paraphraser": "• ZeroGPT AI Paraphraser: Features quick and deep-thinking rephrasing with multilingual support.",
    "signed": "The word signed can be a verb or an adjective with several different meanings depending on the context:",
}
FROM_ARTICLE = [
    "mandate", "constituencies", "restoke", "constituents",  # the four words marked new in Homework 4
    "seats", "backed", "swing", "shifted", "boost", "divides", "stance",  # several meanings
    "bolster", "wary", "fraught", "sovereignty", "resonated",  # harder vocabulary
]


def sentence_with(word):
    pattern = re.compile(r"\b" + word + r"\b", re.IGNORECASE)
    return next(sentence for sentence in split_sentences(ARTICLE) if pattern.search(sentence))


words = [{"word": word, "sentence": sentence} for word, sentence in FROM_CARDS.items()]
words += [{"word": word, "sentence": sentence_with(word)} for word in FROM_ARTICLE]
words.append({"word": "skew", "sentence": SKEW})
Path("spike/meanings/words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(words), "words")

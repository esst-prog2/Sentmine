"""Find the words in a sentence."""

import re
from dataclasses import dataclass

# A word is a run of letters (any alphabet) with apostrophes allowed inside it.
_WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")
_TOKEN = re.compile(r"\S+")


@dataclass(frozen=True)
class Word:
    text: str  # lower case, straight apostrophes
    start: int  # where it starts in the sentence
    end: int  # where it ends in the sentence
    ignored: bool = False  # a token with a digit: counted, but never a real word


def find_words(sentence: str) -> list[Word]:
    """Words of a sentence in order; a token containing a digit comes back as one ignored word."""
    found: list[Word] = []
    for token in _TOKEN.finditer(sentence):
        chunk = token.group()
        if any(ch.isdigit() for ch in chunk):
            found.append(Word(chunk.lower(), token.start(), token.end(), ignored=True))
            continue
        for match in _WORD.finditer(chunk):
            text = match.group().replace("’", "'").lower()
            found.append(Word(text, token.start() + match.start(), token.start() + match.end()))
    return found

"""Classify every word of a passage as common, known, repeat or card."""

from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources

from sentmine.sentences import split_sentences
from sentmine.stem import stem
from sentmine.words import find_words


@lru_cache(maxsize=1)
def load_stopwords() -> frozenset[str]:
    """The built-in common-word list; lines starting with # are comments."""
    text = resources.files("sentmine").joinpath("data/stopwords.txt").read_text(encoding="utf-8")
    words = (line.strip().lower() for line in text.splitlines())
    return frozenset(w for w in words if w and not w.startswith("#"))


def known_stems(lines: Iterable[str]) -> frozenset[str]:
    """Stems of the known words, one word per line; blank lines are ignored.

    Each line goes through the same word finder as the passage, so `Dog`, `dog's`
    and `sighed` are compared the way the passage words are.
    """
    stems = set()
    for line in lines:
        for word in find_words(line.strip()):
            if not word.ignored:
                stems.add(stem(word.text))
    return frozenset(stems)


def parse_known(text: str) -> frozenset[str]:
    """Stems of the known words in the text of a known-words file."""
    return known_stems(text.splitlines())


@dataclass(frozen=True)
class Card:
    word: str  # the word as it first appeared, lower-cased
    sentence: str  # the sentence it first appeared in


@dataclass(frozen=True)
class Analysis:
    """What one passage came to: every word occurrence is in exactly one of the four counts."""

    sentences: int
    words: int
    common: int  # stopwords, too-short words and tokens with a digit
    known: int
    repeats: int
    cards: tuple[Card, ...]  # in order of first appearance

    @property
    def new_words(self) -> int:
        return len(self.cards)


def analyse(text: str, known_words: Iterable[str] = (), min_len: int = 3) -> Analysis:
    """Sort every word occurrence of the passage into common, known, repeat or card."""
    stopwords = load_stopwords()
    known = known_stems(known_words)
    seen: set[str] = set()
    cards: list[Card] = []
    sentences = words = common = known_count = repeats = 0
    for sentence in split_sentences(text):
        sentences += 1
        for word in find_words(sentence):
            words += 1
            letters = len(word.text.replace("'", ""))
            if word.ignored or word.text in stopwords or letters < min_len:
                common += 1
                continue
            key = stem(word.text)
            if key in known:
                known_count += 1
            elif key in seen:
                repeats += 1
            else:
                seen.add(key)
                cards.append(Card(word.text, sentence))
    return Analysis(sentences, words, common, known_count, repeats, tuple(cards))

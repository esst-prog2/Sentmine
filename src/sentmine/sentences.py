"""Split a passage into sentences.

The whole rule, as in openspec/specs/passage-analysis ("Sentence splitting"):
a sentence ends at `.`, `!` or `?` (with any closing quotation marks or
brackets after it) that is followed by whitespace or the end of the paragraph,
unless
  1. it is the full stop of an abbreviation in ABBREVIATIONS (`Dr.`), or
  2. it is a `!` or `?` followed by a lowercase word (`"Stop!" she said.`), or
  3. a quotation opened in this sentence is still open (the quote is kept whole).
A blank line always ends a sentence.
"""

import re

# . ! or ? (one or more), then any closing quotes or brackets, then whitespace or the end.
_END = re.compile(r"[.!?]+[\"'”’)\]»]*(?=\s|$)")
_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
_LINE_BREAK = re.compile(r"\s*\n\s*")

# A full stop after one of these does not end a sentence.
ABBREVIATIONS = frozenset({"mr.", "mrs.", "ms.", "dr.", "st.", "vs.", "etc.", "e.g.", "i.e."})
_OPENING = "\"'“‘(["
# Quotation marks that come in pairs. ‘ and ’ are left out: ’ is also the apostrophe.
_OPENING_QUOTES = "“«"
_CLOSING_QUOTES = "”»"


def _is_abbreviation(paragraph: str, end_mark: re.Match) -> bool:
    """True when the mark is a single full stop that closes an abbreviation such as `Dr.`."""
    if end_mark.group().rstrip("\"'”’)]»") != ".":
        return False
    token = paragraph[: end_mark.start() + 1].rsplit(None, 1)[-1]
    return token.lstrip(_OPENING).lower() in ABBREVIATIONS


def _continues_in_lowercase(paragraph: str, end_mark: re.Match) -> bool:
    """True for `"Stop!" she said.`: a ! or ? followed by a lowercase word."""
    if not ({"!", "?"} & set(end_mark.group())):
        return False
    return paragraph[end_mark.end() :].lstrip()[:1].islower()


def _inside_a_quotation(so_far: str) -> bool:
    """True when `so_far`, the sentence up to and including the mark, leaves quoted speech open."""
    opened = sum(so_far.count(mark) for mark in _OPENING_QUOTES)
    closed = sum(so_far.count(mark) for mark in _CLOSING_QUOTES)
    return opened > closed or so_far.count('"') % 2 == 1


def paragraphs(text: str) -> list[str]:
    """The paragraphs of a text: split at blank lines, each joined onto one line, empty ones dropped."""
    found = []
    for paragraph in _PARAGRAPH_BREAK.split(text.replace("\r\n", "\n").replace("\r", "\n")):
        paragraph = _LINE_BREAK.sub(" ", paragraph.strip())
        if paragraph:
            found.append(paragraph)
    return found


def split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for paragraph in paragraphs(text):
        start = 0
        for end_mark in _END.finditer(paragraph):
            if _is_abbreviation(paragraph, end_mark) or _continues_in_lowercase(paragraph, end_mark):
                continue
            if _inside_a_quotation(paragraph[start : end_mark.end()]):
                continue  # the quote is kept whole, with the words that introduce it
            sentences.append(paragraph[start : end_mark.end()].strip())
            start = end_mark.end()
        rest = paragraph[start:].strip()
        if rest:
            sentences.append(rest)
    return sentences

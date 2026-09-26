"""Split a passage into sentences."""

import re

# . ! or ? (one or more), then any closing quotes or brackets, then whitespace or the end.
_END = re.compile(r"[.!?]+[\"'”’)\]»]*(?=\s|$)")
_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
_LINE_BREAK = re.compile(r"\s*\n\s*")

# A full stop after one of these does not end a sentence.
ABBREVIATIONS = frozenset({"mr.", "mrs.", "ms.", "dr.", "st.", "vs.", "etc.", "e.g.", "i.e."})
_OPENING = "\"'“‘(["


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


def split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for paragraph in _PARAGRAPH_BREAK.split(text.replace("\r\n", "\n").replace("\r", "\n")):
        paragraph = _LINE_BREAK.sub(" ", paragraph.strip())
        if not paragraph:
            continue
        start = 0
        for end_mark in _END.finditer(paragraph):
            if _is_abbreviation(paragraph, end_mark) or _continues_in_lowercase(paragraph, end_mark):
                continue
            sentences.append(paragraph[start : end_mark.end()].strip())
            start = end_mark.end()
        rest = paragraph[start:].strip()
        if rest:
            sentences.append(rest)
    return sentences

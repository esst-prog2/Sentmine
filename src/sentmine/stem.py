"""A crude stem, used only to decide whether two words are the same word.

The stem is never shown to the user, so it does not have to be a real word
(refused -> "refus"). It only has to come out the same for forms of one word.
"""

_VOWELS = set("aeiouy")
_UNDOUBLE = set("bdgmnprt")


def _strip_suffix(word: str, suffix: str) -> str:
    """Drop `suffix` if a vowel remains, then undouble a final consonant (stopp -> stop)."""
    stem = word[: -len(suffix)]
    if not (_VOWELS & set(stem)):
        return word
    if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] in _UNDOUBLE:
        stem = stem[:-1]
    return stem


def stem(word: str) -> str:
    word = word.lower().replace("’", "'")
    if word.endswith("'s"):  # rule 1
        word = word[:-2]
    if len(word) > 4 and word.endswith(("ies", "ied")):  # rule 2
        word = word[:-3] + "y"
    elif len(word) > 5 and word.endswith("ing"):  # rule 3
        word = _strip_suffix(word, "ing")
    elif len(word) > 4 and word.endswith("ed"):  # rule 4
        word = _strip_suffix(word, "ed")
    elif len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):  # rule 5
        word = word[:-1]
    if word.endswith("e"):  # rule 6
        word = word[:-1]
    return word

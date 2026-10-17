"""The base form of an English word (its lemma), used to decide whether two words are the same word.

The reading app and its history use this; the first design's command-line tool keeps
the stem rules in stem.py, so that its numbers from the Homework 4 spike do not change.
"""

import simplemma


def base_form(word: str) -> str:
    """`sighed` -> `sigh`, `ran` -> `run`, `children` -> `child`.

    simplemma looks at the word alone, not its sentence, so `saw` always gives `see`.
    A word it does not know comes back unchanged, lower-cased.
    """
    word = word.lower().replace("’", "'")
    return simplemma.lemmatize(word, lang="en").lower()

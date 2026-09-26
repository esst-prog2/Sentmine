import pytest

from sentmine.stem import stem


@pytest.mark.parametrize(
    "a, b",
    [
        ("sighed", "sigh"),
        ("moved", "move"),
        ("moves", "move"),
        ("moving", "move"),
        ("stopped", "stop"),
        ("stopping", "stop"),
        ("studied", "study"),
        ("studies", "study"),
        ("dogs", "dog"),
        ("dog's", "dog"),
        ("refused", "refuse"),
        ("boxes", "box"),
    ],
)
def test_forms_of_one_word_share_a_stem(a, b):
    assert stem(a) == stem(b)


@pytest.mark.parametrize("word", ["class", "status", "analysis", "need", "spring", "bring", "thing"])
def test_words_that_must_not_be_shortened_to_another_word(word):
    # the stem may lose a final -e, but these have none, so they must come back whole
    assert stem(word) == word


def test_words_without_a_matching_suffix_are_kept():
    assert stem("stubborn") == "stubborn"
    assert stem("equally") == "equally"
    assert stem("resilient") == "resilient"


def test_irregular_forms_do_not_match():
    assert stem("ran") != stem("run")


def test_rule_order_examples():
    assert stem("sighed") == "sigh"
    assert stem("refused") == "refus"
    assert stem("moved") == "mov"
    assert stem("stopped") == "stop"
    assert stem("studied") == "study"


def test_ing_needs_a_vowel_to_remain():
    assert stem("spring") == "spring"  # not "spr"
    assert stem("flying") == "fly"


def test_curly_possessive_is_dropped_too():
    assert stem("dog’s") == "dog"


def test_stem_is_case_insensitive():
    assert stem("Sighed") == stem("sighed")

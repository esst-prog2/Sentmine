import pytest

from sentmine.words import find_words


def texts(sentence):
    return [w.text for w in find_words(sentence)]


def test_contraction_stays_whole():
    assert texts("I don't know.") == ["i", "don't", "know"]


def test_curly_apostrophe_is_the_same_word():
    assert texts("I don’t know.") == ["i", "don't", "know"]


def test_hyphenated_word_is_split_into_two_words():
    assert texts("A well-known dog.") == ["a", "well", "known", "dog"]


@pytest.mark.parametrize("token", ["2026", "3rd", "COVID-19"])
def test_token_with_a_digit_is_one_ignored_word(token):
    words = find_words(f"In {token} it rained.")
    ignored = [w for w in words if w.ignored]
    assert len(ignored) == 1
    assert ignored[0].text == token.lower()
    assert [w.text for w in words if not w.ignored] == ["in", "it", "rained"]


def test_accented_letters_stay_in_one_word():
    assert texts("A small café.") == ["a", "small", "café"]


def test_quotes_at_the_edges_are_stripped():
    assert texts("'stubborn' and “resilient”") == ["stubborn", "and", "resilient"]


def test_trailing_apostrophe_of_a_plural_possessive_is_dropped():
    assert texts("the dogs' owner") == ["the", "dogs", "owner"]


def test_words_are_lower_cased():
    assert texts("Stubborn DOG") == ["stubborn", "dog"]


def test_punctuation_alone_is_not_a_word():
    assert texts("Wait — what ... ?") == ["wait", "what"]


def test_positions_point_at_the_original_text():
    sentence = "Its Stubborn dog."
    stubborn = find_words(sentence)[1]
    assert sentence[stubborn.start : stubborn.end] == "Stubborn"


def test_positions_inside_a_hyphenated_token():
    sentence = "a well-known dog"
    known = find_words(sentence)[2]
    assert sentence[known.start : known.end] == "known"

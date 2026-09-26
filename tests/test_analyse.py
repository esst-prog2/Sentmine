import random

import pytest

from sentmine.analyse import analyse


def card_words(result):
    return [card.word for card in result.cards]


def test_demo_passage_gives_the_numbers_in_the_spec(demo_passage, demo_known, demo_expected):
    result = analyse(demo_passage, demo_known)
    e = demo_expected
    assert (result.sentences, result.words) == (e.sentences, e.words)
    assert (result.common, result.known, result.repeats) == (e.common, e.known, e.repeats)
    assert len(result.cards) == e.cards
    assert card_words(result) == e.card_words


def test_demo_cards_use_the_sentence_they_first_appeared_in(demo_passage, demo_known):
    by_word = {c.word: c.sentence for c in analyse(demo_passage, demo_known).cards}
    first = "The stubborn old dog refused to move."
    third = "She was resilient, but the dog was equally stubborn."
    assert by_word == {
        "refused": first,
        "stubborn": first,
        "sighed": "Its owner sighed.",
        "resilient": third,
        "equally": third,
    }


def test_repeat_is_collapsed_and_uses_the_first_sentence():
    result = analyse("A stubborn dog. Another stubborn cat.", [])
    stubborn = [c for c in result.cards if c.word == "stubborn"]
    assert len(stubborn) == 1 and stubborn[0].sentence == "A stubborn dog."
    assert result.repeats == 1


def test_repeat_inside_one_sentence():
    result = analyse("It was stubborn and stubborn.", [])
    assert card_words(result) == ["stubborn"]
    assert result.repeats == 1


def test_different_forms_of_one_word_make_one_card_with_the_first_form():
    result = analyse("Sigh. Then she sighed.", [])
    assert card_words(result) == ["sigh"]
    assert result.repeats == 1


def test_known_stem_matches_an_inflected_form():
    result = analyse("Then she sighed.", ["sigh"])
    assert result.cards == () and result.known == 1


def test_known_word_is_the_inflected_form():
    result = analyse("Then she sigh.", ["sighed"])
    assert result.cards == () and result.known == 1


def test_possessive_of_a_known_word_is_known():
    assert analyse("The dog's bowl.", ["dog"]).known == 1


def test_known_words_are_case_insensitive():
    assert analyse("The dog barked.", ["Dog"]).known == 1


def test_known_word_that_is_new_elsewhere_is_only_skipped_where_it_matches():
    result = analyse("Moved and move and moving.", ["move"])
    assert result.known == 3 and result.cards == ()


def test_irregular_form_is_new():
    assert card_words(analyse("She ran home.", ["run"])) == ["ran", "home"]


# --- 4.3: counts always add up, and the special cases ---------------------------------


PASSAGES = [
    "",
    "   \n\n  ",
    "The. A. To.",
    "Only common words are here, so it seems.",
    "The stubborn old dog refused to move. Its owner sighed.\nShe was resilient, but the dog was equally stubborn.",
    "In 2026 the COVID-19 rules of 3rd class were well-known. Don't stop.",
    "Dr. Lee said \"Stop!\" she said. Caf\u00e9s and na\u00efve r\u00e9sum\u00e9s are fine.",
    "sigh sighed sighs sighing sigh SIGH Sigh",
    "one\n\ntwo\n\nthree three three",
    "It's the dog's bowl; the dogs' bowls; doesn\u2019t matter.",
]


@pytest.mark.parametrize("text", PASSAGES)
@pytest.mark.parametrize("known", [[], ["dog", "sigh", "bowl"]])
@pytest.mark.parametrize("min_len", [1, 3, 5])
def test_every_word_is_counted_exactly_once(text, known, min_len):
    r = analyse(text, known, min_len)
    assert r.words == r.common + r.known + r.repeats + len(r.cards)


def test_counts_add_up_on_random_passages():
    vocabulary = (
        "the a to dog dogs old stubborn stubborn sigh sighed sighing move moved resilient "
        "well-known 2026 COVID-19 don't it's caf\u00e9 Anna equally refused . ! ? , \" ( ) -- Dr. e.g."
    ).split()
    rng = random.Random(20260926)
    for _ in range(300):
        text = " ".join(rng.choice(vocabulary) for _ in range(rng.randint(0, 40)))
        known = rng.sample(["dog", "old", "sigh", "move", "the", "anna"], rng.randint(0, 4))
        r = analyse(text, known, rng.randint(1, 6))
        assert r.words == r.common + r.known + r.repeats + len(r.cards), text


def test_min_len_5_ignores_dog_even_if_it_is_not_known():
    r = analyse("The dog barked loudly.", [], min_len=5)
    assert "dog" not in card_words(r)
    assert card_words(r) == ["barked", "loudly"]
    assert r.common == 2  # "the" and "dog"


def test_default_min_len_keeps_three_letter_words():
    assert "dog" in card_words(analyse("A dog barked.", []))


def test_stopword_listed_in_known_counts_as_common_not_known():
    r = analyse("The dog barked.", ["the"])
    assert r.common == 1 and r.known == 0
    assert card_words(r) == ["dog", "barked"]


def test_a_name_becomes_a_card():
    r = analyse("Anna sighed.", [])
    assert card_words(r) == ["anna", "sighed"]


def test_token_with_a_digit_counts_as_common_never_a_card():
    r = analyse("In 2026 it rained.", [])
    assert r.words == 4 and r.common == 3  # "in", "2026", "it"
    assert card_words(r) == ["rained"]


def test_hyphenated_word_is_two_words():
    assert card_words(analyse("A well-known dog.", [])) == ["well", "known", "dog"]


def test_cards_are_in_order_of_first_appearance():
    assert card_words(analyse("Zebra apple mango zebra.", [])) == ["zebra", "apple", "mango"]


def test_empty_passage():
    r = analyse("", [])
    assert (r.sentences, r.words, r.common, r.known, r.repeats, r.cards) == (0, 0, 0, 0, 0, ())


def test_only_common_and_known_words_leave_no_cards():
    r = analyse("The dog is old.", ["dog", "old"])
    assert r.cards == ()

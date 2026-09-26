from sentmine.analyse import known_stems, parse_known
from sentmine.stem import stem


def test_inflected_form_of_a_known_word():
    assert stem("sighed") in known_stems(["sigh"])


def test_known_word_is_the_inflected_form():
    assert stem("sigh") in known_stems(["sighed"])


def test_possessive_matches_the_known_word():
    assert stem("dog's") in known_stems(["dog"])


def test_known_words_match_case_insensitively():
    assert stem("dog") in known_stems(["Dog"])
    assert stem("Dog") in known_stems(["dog"])


def test_blank_lines_and_surrounding_whitespace_are_ignored():
    stems = parse_known("dog\n\n   old  \n\t\n")
    assert stems == frozenset({"dog", "old"})


def test_windows_line_endings_are_fine():
    assert parse_known("dog\r\nold\r\n") == frozenset({"dog", "old"})


def test_an_empty_file_knows_nothing():
    assert parse_known("") == frozenset()


def test_a_line_with_a_digit_is_not_a_known_word():
    assert parse_known("2026\n") == frozenset()


def test_demo_known_words(demo_known):
    assert known_stems(demo_known) == frozenset({"dog", "old", "mov", "owner"})

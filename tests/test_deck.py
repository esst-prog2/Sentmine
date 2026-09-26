import json

import pytest
from apkg_helper import read_notes

from sentmine.analyse import Card
from sentmine.deck import card_back, card_front, deck_id_for, write_deck

DEMO_SENTENCE = "The stubborn old dog refused to move."


def test_front_has_the_word_in_bold_and_nothing_else_changed():
    assert card_front(DEMO_SENTENCE, "stubborn") == "The <b>stubborn</b> old dog refused to move."


def test_back_is_the_word():
    assert card_back("stubborn") == "stubborn"


def test_every_occurrence_in_the_sentence_is_bold():
    front = card_front("The stubborn dog was stubborn.", "stubborn")
    assert front == "The <b>stubborn</b> dog was <b>stubborn</b>."


def test_original_letter_case_is_kept_on_the_front():
    front = card_front("Stubborn dogs sulk.", "stubborn")
    assert front == "<b>Stubborn</b> dogs sulk."
    assert card_back("stubborn") == "stubborn"


def test_special_characters_are_escaped_so_they_display_as_typed():
    front = card_front("AT&T said x < y.", "said")
    assert front == "AT&amp;T <b>said</b> x &lt; y."


def test_part_of_a_longer_word_is_not_bold():
    assert card_front("The dogged dog.", "dog") == "The dogged <b>dog</b>."


def test_possessive_is_a_different_word_from_the_bare_word():
    assert card_front("The dog's dog.", "dog") == "The dog's <b>dog</b>."


def test_only_the_card_word_is_bold_inside_a_hyphenated_word():
    assert card_front("A well-known dog.", "known") == "A well-<b>known</b> dog."


def test_curly_apostrophe_word_is_matched_and_kept_as_typed():
    assert card_front("It doesn’t matter.", "doesn't") == "It <b>doesn’t</b> matter."


def test_quotes_are_left_alone():
    assert card_front('"Stop!" she said.', "said") == '"Stop!" she <b>said</b>.'


def test_a_word_that_is_not_in_the_sentence_leaves_it_alone():
    assert card_front("A sentence.", "zebra") == "A sentence."


# --- the .apkg file ---------------------------------------------------------

DEMO_CARDS = [
    Card("refused", "The stubborn old dog refused to move."),
    Card("stubborn", "The stubborn old dog refused to move."),
    Card("sighed", "Its owner sighed."),
    Card("resilient", "She was resilient, but the dog was equally stubborn."),
    Card("equally", "She was resilient, but the dog was equally stubborn."),
]


def test_deck_holds_one_note_per_card_with_front_and_back(tmp_path):
    out = tmp_path / "new.apkg"
    write_deck(DEMO_CARDS, out)
    notes, _ = read_notes(out, tmp_path)
    assert len(notes) == 5
    by_back = {back: front for _guid, front, back in notes}
    assert by_back["stubborn"] == "The <b>stubborn</b> old dog refused to move."
    assert by_back["sighed"] == "Its owner <b>sighed</b>."


def test_no_partial_file_is_left_behind(tmp_path):
    write_deck(DEMO_CARDS, tmp_path / "new.apkg")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["new.apkg"]


def test_writing_to_a_missing_folder_fails_and_leaves_nothing(tmp_path):
    with pytest.raises(OSError):
        write_deck(DEMO_CARDS, tmp_path / "missing" / "new.apkg")
    assert list(tmp_path.iterdir()) == []


def test_same_cards_give_the_same_note_ids_and_deck_id(tmp_path):
    first = tmp_path / "a" / "new.apkg"
    second = tmp_path / "b" / "new.apkg"
    first.parent.mkdir()
    second.parent.mkdir()
    write_deck(DEMO_CARDS, first)
    write_deck(DEMO_CARDS, second)
    notes_a, decks_a = read_notes(first, first.parent)
    notes_b, decks_b = read_notes(second, second.parent)
    assert [n[0] for n in notes_a] == [n[0] for n in notes_b]
    assert list(json.loads(decks_a)) == list(json.loads(decks_b))


def test_deck_id_depends_on_the_deck_name_and_is_in_range():
    assert deck_id_for("new") == deck_id_for("new")
    assert deck_id_for("new") != deck_id_for("other")
    assert (1 << 30) <= deck_id_for("new") < (1 << 31)


def test_deck_has_the_file_name_as_its_name(tmp_path):
    out = tmp_path / "passage.apkg"
    write_deck(DEMO_CARDS, out)
    _notes, decks = read_notes(out, tmp_path)
    assert "passage" in [d["name"] for d in json.loads(decks).values()]

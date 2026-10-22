"""Base forms, and reading the old history file (history.jsonl) so its cards can move into the database."""

import json

import pytest

from sentmine.history import Entry, HistoryProblem, read_history_file
from sentmine.lemma import base_form

SIGHED = Entry("word", "sigh", "Its owner sighed.", "sighed (sigh)", "sighed", "2026-10-17")
SD = Entry("definition", "standard deviation", "standard deviation", "How spread out the values are.", "", "2026-10-09")


def line(entry):
    return json.dumps({name: getattr(entry, name) for name in entry.__dataclass_fields__}) + "\n"


# --- base forms -------------------------------------------------------------------


@pytest.mark.parametrize(
    "word, base",
    [("sighed", "sigh"), ("ran", "run"), ("went", "go"), ("children", "child"), ("skewed", "skew"),
     ("Sighed", "sigh"), ("dog’s", "dog"), ("skew", "skew")],
)
def test_base_form(word, base):
    assert base_form(word) == base


def test_hoped_and_hopped_are_different_words():
    assert base_form("hoped") == "hope"
    assert base_form("hopped") == "hop"


def test_an_unknown_word_comes_back_lower_cased():
    assert base_form("Xyzzyed") == "xyzzyed"


# --- reading the old history file --------------------------------------------------------


def test_a_missing_file_has_no_cards(tmp_path):
    assert read_history_file(tmp_path / "history.jsonl") == []


def test_the_cards_come_back_in_order(tmp_path):
    path = tmp_path / "history.jsonl"
    path.write_text(line(SIGHED) + "\n" + line(SD), encoding="utf-8")  # a blank line is skipped
    assert read_history_file(path) == [SIGHED, SD]


@pytest.mark.parametrize(
    "content",
    ["not json at all\n", '{"kind": "word"}\n', '{"kind": 1, "key": "a", "front": "a", "back": "a", "word": "a", "date": "x"}\n'],
)
def test_a_line_that_is_not_a_card_is_reported_with_its_number(tmp_path, content):
    path = tmp_path / "history.jsonl"
    path.write_text(line(SIGHED) + content, encoding="utf-8")
    with pytest.raises(HistoryProblem, match="line 2 is not a card"):
        read_history_file(path)


def test_a_file_that_is_not_text_is_reported(tmp_path):
    path = tmp_path / "history.jsonl"
    path.write_bytes(b"\xff\xfe\x00broken")
    with pytest.raises(HistoryProblem, match="could not be read"):
        read_history_file(path)

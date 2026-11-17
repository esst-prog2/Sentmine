"""met-again: how many texts a remembered card's word or term was met again in."""

import sqlite3
from datetime import date

import pytest
from reading_helper import place_of

from sentmine.app import create_app
from sentmine.history import Entry
from sentmine.memory import SCHEMA_VERSION, CardMemory
from sentmine.reading import Session

TODAY = date.today().isoformat()
FIRST = "Outliers can skew it considerably."
SECOND = "Heavy tails skewed the mean."
THIRD = "Income data skew to the right."


@pytest.fixture
def memory(tmp_path):
    return CardMemory(tmp_path / "cards.db")


def made_from_first(memory, tmp_path):
    """A card for `skew`, made from the first text and downloaded, as the reader would."""
    session = Session(memory)
    session.load(FIRST)
    session.pick_word(*place_of(session, "skew"))
    session.export(tmp_path / "new.apkg")


def read(memory, text):
    return create_app(Session(memory)).test_client().post("/api/text", json={"text": text}).get_json()


def test_a_word_met_in_a_new_text(memory, tmp_path):
    made_from_first(memory, tmp_path)
    read(memory, SECOND)
    assert memory.met_again() == {("word", "skew"): (1, TODAY)}


def test_the_same_text_twice_counts_once(memory, tmp_path):
    made_from_first(memory, tmp_path)
    read(memory, SECOND)
    read(memory, SECOND)
    assert memory.met_again() == {("word", "skew"): (1, TODAY)}


def test_the_text_the_card_came_from_does_not_count(memory, tmp_path):
    made_from_first(memory, tmp_path)
    read(memory, FIRST)
    assert memory.met_again() == {}


def test_the_text_read_before_the_card_was_made_does_not_count_either(memory, tmp_path):
    memory.add([Entry("word", "skew", THIRD, "skew", "skew", "2026-11-01")])
    read(memory, FIRST)  # the card is met here first...
    assert memory.met_again() == {("word", "skew"): (1, TODAY)}
    session = Session(memory)  # ...then the reader makes another card from it anyway
    session.load(FIRST)
    session.pick_word(*place_of(session, "skew"), anyway=True)
    session.export(tmp_path / "new.apkg")
    assert memory.met_again() == {}


def test_a_card_sent_to_anki_marks_its_text_too(memory):
    client = create_app(Session(memory), send=lambda notes, deck: (len(notes), 0)).test_client()
    client.post("/api/text", json={"text": FIRST})
    client.post("/api/word", json={"sentence": 0, "word": 2})
    client.post("/api/send", json={"deck": "new"})
    client.post("/api/text", json={"text": FIRST})
    assert memory.met_again() == {}


def test_many_places_in_one_text_count_once(memory):
    memory.add([Entry("definition", "confounder", "confounder", "A common cause.", "", "2026-11-08")])
    read(memory, " ".join(["A confounder hides here."] * 40))
    assert memory.met_again() == {("definition", "confounder"): (1, TODAY)}


def test_my_cards_shows_the_line(memory, tmp_path):
    made_from_first(memory, tmp_path)
    read(memory, SECOND)
    read(memory, THIRD)
    cards = create_app(Session(memory)).test_client().get("/api/memory").get_json()["cards"]
    assert cards[0]["met_again"] == f"Met again in 2 texts, last on {TODAY}"


def test_one_text_in_the_singular_and_none_shows_nothing(memory, tmp_path):
    made_from_first(memory, tmp_path)
    memory.add([Entry("word", "tail", "Heavy tails.", "tail", "tail", "2026-11-01")])
    read(memory, THIRD)
    cards = create_app(Session(memory)).test_client().get("/api/memory").get_json()["cards"]
    assert sorted(card["met_again"] for card in cards) == ["", f"Met again in 1 text, last on {TODAY}"]


def test_the_card_shown_when_pointing_has_the_line(memory, tmp_path):
    made_from_first(memory, tmp_path)
    read(memory, SECOND)
    state = read(memory, THIRD)
    assert state["known_cards"]["skew"]["met_again"] == f"Met again in 2 texts, last on {TODAY}"


def test_a_memory_of_layout_2_is_brought_up_keeping_its_cards(tmp_path):
    path = tmp_path / "cards.db"
    words = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
    CardMemory(path).add([Entry("word", w, f"The {w} front.", w, w, "2026-11-01") for w in words])
    with sqlite3.connect(path) as db:  # make it look like a memory from before this change
        db.execute("DROP TABLE meetings")
        db.execute("PRAGMA user_version = 2")
    memory = CardMemory(path)
    with sqlite3.connect(path) as db:
        version = db.execute("PRAGMA user_version").fetchone()[0]
    assert (memory.problem, version, memory.count()) == ("", SCHEMA_VERSION, 10)
    read(memory, "A text with delta in it.")
    assert memory.met_again() == {("word", "delta"): (1, TODAY)}


def test_deleting_the_last_card_deletes_its_meetings(memory, tmp_path):
    made_from_first(memory, tmp_path)
    read(memory, SECOND)
    card_id = memory.search()[0][0].id
    memory.delete(card_id)
    assert memory.met_again() == {}
    memory.add([Entry("word", "skew", THIRD, "skew", "skew", "2026-11-14")])
    assert memory.met_again() == {}


def test_deleting_one_of_two_cards_keeps_the_meetings(memory, tmp_path):
    made_from_first(memory, tmp_path)
    memory.add([Entry("word", "skew", THIRD, "skew (again)", "skew", "2026-11-14")])
    read(memory, SECOND)
    memory.delete(memory.search()[0][0].id)
    assert memory.met_again() == {("word", "skew"): (1, TODAY)}

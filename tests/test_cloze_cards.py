"""cloze-cards. Passages are invented by hand; Anki is the fake AnkiConnect from test_send_to_anki."""

import sqlite3

import pytest
from apkg_helper import read_notes
from reading_helper import place_of
from test_send_to_anki import FakeAnki, via

from sentmine.app import create_app
from sentmine.deck import CLOZE_MODEL, CLOZE_MODEL_ID, MODEL_ID
from sentmine.memory import CardMemory
from sentmine.reading import Problem, Session

PASSAGE = "The standard deviation measures how spread out a set of values is."


@pytest.fixture
def session():
    return Session()


# --- the card ------------------------------------------------------------------------------------


def test_the_term_is_in_the_passage(session):
    _, card = session.add_definition("standard deviation", PASSAGE)
    assert card.cloze
    assert card.front_html == "The [...] measures how spread out a set of values is."
    assert card.back_html == "The <b>standard deviation</b> measures how spread out a set of values is."


def test_a_word_that_only_contains_the_term(session):
    _, card = session.add_definition("variance", "The covariance of two variables.")
    assert not card.cloze and not card.can_cloze


def test_the_term_is_found_ignoring_case_and_every_place_is_hidden(session):
    _, card = session.add_definition("variance", "Variance is spread. The variance is never negative.")
    assert card.front_html == "[...] is spread. The [...] is never negative."
    assert card.note.fields[0] == "{{c1::Variance}} is spread. The {{c1::variance}} is never negative."


def test_switching_gives_the_card_as_before(session):
    _, card = session.add_definition("standard deviation", PASSAGE)
    session.set_cloze(card.id, False)
    assert (card.front_html, card.back_html) == ("standard deviation", PASSAGE)
    assert card.note.fields == ("standard deviation", PASSAGE) and not card.note.cloze


def test_switching_on_without_the_term_is_refused(session):
    _, card = session.add_definition("variance", "The covariance of two variables.")
    with pytest.raises(Problem, match="nothing to hide"):
        session.set_cloze(card.id, True)
    assert not card.cloze


def test_a_word_card_cannot_be_a_cloze_card(session):
    session.load("Polls skew young.")
    _, card = session.pick_word(*place_of(session, "skew"))
    with pytest.raises(Problem, match="Only definition cards"):
        session.set_cloze(card.id, True)


def test_an_edit_that_removes_the_term_makes_it_term_to_passage(session):
    _, card = session.add_definition("standard deviation", PASSAGE)
    session.edit(card.id, "standard deviation", "A measure of spread.")
    assert not card.cloze


def test_an_edit_that_keeps_the_term_keeps_cloze(session):
    _, card = session.add_definition("standard deviation", PASSAGE)
    session.edit(card.id, "standard deviation", "The standard deviation is a measure of spread.")
    assert card.cloze and card.front_html == "The [...] is a measure of spread."


def test_html_in_the_passage_is_escaped_around_the_gap(session):
    _, card = session.add_definition("mean", "The mean of <x> & y.")
    assert card.note.fields[0] == "The {{c1::mean}} of &lt;x&gt; &amp; y."


# --- Download and Send ---------------------------------------------------------------------------


def note_types_in(apkg, folder):
    read_notes(apkg, folder)
    db = sqlite3.connect(folder / "collection.anki2")
    try:
        return [mid for (mid,) in db.execute("select mid from notes order by id")]
    finally:
        db.close()


def test_downloading_a_cloze_card(session, tmp_path):
    session.add_definition("standard deviation", PASSAGE)
    session.export(tmp_path / "new.apkg")
    notes, _ = read_notes(tmp_path / "new.apkg", tmp_path)
    assert notes[0][1] == "The {{c1::standard deviation}} measures how spread out a set of values is."
    assert note_types_in(tmp_path / "new.apkg", tmp_path) == [CLOZE_MODEL_ID]


def test_a_deck_with_both_kinds_has_both_note_types(session, tmp_path):
    session.load("Polls skew young.")
    session.pick_word(*place_of(session, "skew"))
    session.add_definition("standard deviation", PASSAGE)
    session.export(tmp_path / "new.apkg")
    assert note_types_in(tmp_path / "new.apkg", tmp_path) == [MODEL_ID, CLOZE_MODEL_ID]


def test_sending_both_kinds_makes_both_note_types(session):
    session.load("Polls skew young.")
    session.pick_word(*place_of(session, "skew"))
    session.add_definition("standard deviation", PASSAGE)
    fake = FakeAnki(note_types=[])
    assert session.send("stats", via(fake))[:2] == (2, 0)
    assert sorted(fake.note_types) == sorted(["sentmine: word in its sentence", CLOZE_MODEL.name])
    assert fake.decks["stats"][1] == "The {{c1::standard deviation}} measures how spread out a set of values is."


def test_switching_and_sending_again_adds_the_other_kind(session):
    _, card = session.add_definition("standard deviation", PASSAGE)
    fake = FakeAnki()
    session.send("stats", via(fake))
    session.set_cloze(card.id, False)
    assert session.send("stats", via(fake))[:2] == (1, 0)


# --- the memory ----------------------------------------------------------------------------------


def test_a_cloze_card_is_remembered_as_a_definition(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    reading = Session(memory)
    reading.add_definition("standard deviation", PASSAGE)
    reading.export(tmp_path / "new.apkg", day="2026-11-03")
    cards, total = memory.search("standard")
    assert total == 1
    assert (cards[0].entry.kind, cards[0].entry.front, cards[0].entry.back) == ("definition", "standard deviation", PASSAGE)


# --- the app -------------------------------------------------------------------------------------


def test_the_route_switches_and_says_so():
    client = create_app().test_client()
    client.post("/api/text", json={"text": PASSAGE})
    made = client.post("/api/definition", json={"term": "standard deviation", "passage": PASSAGE}).get_json()
    card = made["cards"][0]
    assert card["cloze"] and card["can_cloze"]
    off = client.put(f"/api/cards/{card['id']}/cloze", json={"cloze": False}).get_json()
    assert not off["cards"][0]["cloze"] and off["cards"][0]["front_html"] == "standard deviation"
    assert off["message"] == "Now a term → passage card."
    on = client.put(f"/api/cards/{card['id']}/cloze", json={"cloze": True}).get_json()
    assert on["message"] == "Now a cloze card: 'standard deviation' is hidden in the passage."


@pytest.mark.parametrize("body", [{}, {"cloze": "yes"}, {"cloze": 1}])
def test_the_route_needs_true_or_false(body):
    client = create_app().test_client()
    client.post("/api/definition", json={"term": "standard deviation", "passage": PASSAGE})
    assert client.put("/api/cards/1/cloze", json=body).status_code == 400


def test_the_route_refuses_when_the_term_is_not_in_the_passage():
    client = create_app().test_client()
    client.post("/api/definition", json={"term": "variance", "passage": "The covariance of two variables."})
    response = client.put("/api/cards/1/cloze", json={"cloze": True})
    assert response.status_code == 400 and "nothing to hide" in response.get_json()["error"]

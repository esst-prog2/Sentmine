"""known-terms: definition terms that already have cards are marked too."""

import pytest

from sentmine.app import _known_note, create_app
from sentmine.history import Entry
from sentmine.memory import CardMemory
from sentmine.reading import Session

SIMPSON = Entry("definition", "simpson’s reversal", "Simpson’s reversal", "Strangely, the data revealed a Simpson’s reversal.", "", "2026-11-07")
CONFOUNDER = Entry("definition", "confounder", "confounder", "A common cause of treatment and outcome.", "", "2026-11-08")
VARIANCE = Entry("definition", "variance", "variance", "The square of the standard deviation.", "", "2026-11-02")
REVERSAL = Entry("word", "reversal", "A sudden reversal of fortune.", "reversal", "reversal", "2026-11-01")
SKEW = Entry("word", "skew", "Outliers can skew it considerably.", "skew", "skew", "2026-10-29")


@pytest.fixture
def session(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    memory.add([SIMPSON, CONFOUNDER, VARIANCE, REVERSAL, SKEW])
    return Session(memory)


def marked(session, text):
    session.load(text)
    paragraphs = session.layout(session.known_cards(), session.known_terms())
    return [(piece["text"], piece["known"]) for p in paragraphs for s in p for piece in s["pieces"] if "known" in piece]


def test_the_memory_gives_the_latest_card_for_each_term(session):
    assert set(session.memory.term_cards()) == {"simpson’s reversal", "confounder", "variance"}


def test_every_word_of_a_term_is_marked(session):
    assert marked(session, "The data revealed a Simpson’s reversal: although it was odd.") == [
        ("Simpson’s", "term:simpson’s reversal"), ("reversal", "term:simpson’s reversal")]


def test_case_does_not_matter(session):
    assert marked(session, "Confounder bias is common.") == [("Confounder", "term:confounder")]


def test_not_inside_another_word_or_form(session):
    assert marked(session, "The covariance and the variances differ.") == []


def test_a_term_wins_over_a_word_card(session):
    assert marked(session, "A reversal. Then a Simpson’s reversal.") == [
        ("reversal", "reversal"), ("Simpson’s", "term:simpson’s reversal"), ("reversal", "term:simpson’s reversal")]


def test_the_state_has_the_term_card_under_its_own_key(session):
    client = create_app(session).test_client()
    state = client.post("/api/text", json={"text": "A confounder may skew it."}).get_json()
    assert set(state["known_cards"]) == {"term:confounder", "skew"}
    card = state["known_cards"]["term:confounder"]
    assert (card["kind"], card["front_html"], card["date"]) == ("definition", "confounder", "2026-11-08")


@pytest.mark.parametrize("words, terms, note", [
    (3, 0, "3 words you have cards for are underlined."),
    (1, 0, "1 word you have a card for is underlined."),
    (2, 1, "2 words and 1 term you have cards for are underlined."),
    (0, 2, "2 terms you have cards for are underlined."),
    (0, 1, "1 term you have a card for is underlined."),
    (1, 1, "1 word and 1 term you have cards for are underlined."),
])
def test_the_note_counts_words_and_terms(words, terms, note):
    assert _known_note(words, terms) == note


def test_the_message_after_reading_counts_words_and_terms(session):
    client = create_app(session).test_client()
    message = client.post("/api/text", json={"text": "Outliers skew a reversal; a confounder hides a Simpson’s reversal."}).get_json()["message"]
    assert message == "Text loaded. 2 words and 2 terms you have cards for are underlined."

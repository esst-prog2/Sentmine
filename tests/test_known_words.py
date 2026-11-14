"""known-words: words that already have cards are marked when a new text is read."""

import io

import pytest
from pdf_helper import make_pdf
from reading_helper import place_of

from sentmine.app import create_app
from sentmine.history import Entry
from sentmine.memory import CardMemory
from sentmine.reading import Session

SKEW = Entry("word", "skew", "Outliers can skew it considerably.", "skew", "skew", "2026-10-29")
RUN = Entry("word", "run", "They run every day.", "run", "run", "2026-11-01")
VARIANCE = Entry("definition", "variance", "variance", "The square of the standard deviation.", "", "2026-11-02")


@pytest.fixture
def memory(tmp_path):
    remembered = CardMemory(tmp_path / "cards.db")
    remembered.add([SKEW, RUN, VARIANCE])
    return remembered


def marked(paragraphs):
    """(word, base form) of every word piece marked as having a card."""
    return [(piece["text"], piece["known"]) for p in paragraphs for s in p for piece in s["pieces"] if "known" in piece]


# --- the memory and the layout --------------------------------------------------------------------


def test_the_memory_gives_the_latest_word_card_for_each_base_form(memory):
    newer = Entry("word", "skew", "The data skew right.", "skew", "skew", "2026-11-10")
    memory.add([newer])
    cards = memory.word_cards()
    assert set(cards) == {"skew", "run"} and cards["skew"].date == "2026-11-10"


def test_a_word_with_a_card_is_marked(memory):
    session = Session(memory)
    session.load("Outliers can skew it considerably. Nothing else here.")
    assert marked(session.layout(session.known_cards())) == [("skew", "skew")]


def test_another_form_of_the_word_is_marked(memory):
    session = Session(memory)
    session.load("Yesterday they ran home.")
    assert marked(session.layout(session.known_cards())) == [("ran", "run")]


def test_a_definition_term_is_marked_as_a_term_not_a_word(memory):
    session = Session(memory)
    session.load("The variance is never negative.")
    assert marked(session.layout(session.known_cards())) == []  # not as a word
    assert marked(session.layout(session.known_cards(), session.known_terms())) == [("variance", "term:variance")]


def test_a_picked_word_is_shown_as_picked_not_marked(memory):
    session = Session(memory)
    session.load("Outliers can skew it. Skew again.")
    session.pick_word(*place_of(session, "skew"), anyway=True)
    assert marked(session.layout(session.known_cards())) == [("Skew", "skew")]


def test_without_a_memory_nothing_is_marked():
    session = Session()
    session.load("Outliers can skew it considerably.")
    assert session.known_cards() == {} and marked(session.layout(session.known_cards())) == []


def test_a_memory_that_cannot_be_read_marks_nothing(tmp_path):
    folder = tmp_path / "a-folder"
    folder.mkdir()
    broken = CardMemory(folder)  # a folder, not a database file
    assert broken.problem
    session = Session(broken)
    session.load("Outliers can skew it considerably.")
    assert marked(session.layout(session.known_cards())) == []


# --- the app --------------------------------------------------------------------------------------


def test_the_state_has_the_cards_of_the_marked_words_once(memory):
    client = create_app(Session(memory)).test_client()
    state = client.post("/api/text", json={"text": "Skew, skew and skew. They ran."}).get_json()
    assert set(state["known_cards"]) == {"skew", "run"}
    card = state["known_cards"]["skew"]
    assert card["front_html"] == "Outliers can <b>skew</b> it considerably." and card["date"] == "2026-10-29"


@pytest.mark.parametrize("text, message", [
    ("Skew, run and nothing else.", "Text loaded. 2 words you have cards for are underlined."),
    ("Outliers skew it.", "Text loaded. 1 word you have a card for is underlined."),
    ("Nothing known here.", "Text loaded."),
])
def test_the_message_after_reading_counts_the_card_words(memory, text, message):
    client = create_app(Session(memory)).test_client()
    assert client.post("/api/text", json={"text": text}).get_json()["message"] == message


def test_the_message_after_opening_a_pdf_counts_them_too(memory):
    client = create_app(Session(memory)).test_client()
    data = make_pdf([["Outliers can skew the mean."]])
    state = client.post("/api/file", data={"file": (io.BytesIO(data), "notes.pdf")}, content_type="multipart/form-data").get_json()
    assert state["message"] == "Read 1 page. 1 word you have a card for is underlined."


def test_other_answers_do_not_repeat_the_count(memory):
    client = create_app(Session(memory)).test_client()
    client.post("/api/text", json={"text": "Outliers skew it."})
    assert "underlined" not in client.get("/api/state").get_json()["message"]


def test_a_card_sent_now_marks_its_word_elsewhere_in_the_text(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    session = Session(memory)
    client = create_app(session, send=lambda notes, deck: (len(notes), 0)).test_client()
    client.post("/api/text", json={"text": "Outliers can skew it. Later the data skew again."})
    client.post("/api/word", json={"sentence": 0, "word": 2})
    assert marked(session.layout(session.known_cards())) == []
    state = client.post("/api/send", json={"deck": "new"}).get_json()
    words = [(piece["text"], piece.get("known"), piece["picked"]) for p in state["paragraphs"] for s in p
             for piece in s["pieces"] if piece.get("text") == "skew"]
    assert words == [("skew", None, True), ("skew", "skew", False)]

"""A drag over a term makes its card at once with its sentence. While a card is open in Edit, text selected on a
web page waits for it, and its editor puts it at the cursor."""

import pytest
from reading_helper import place_of

from sentmine.app import create_app
from sentmine.reading import Problem, Session

TEXT = ("In analyses of observational studies, the measured confounders are adjusted. "
        "Quantitative techniques are used infrequently.\n\n"
        "A sensitivity analysis asks how strong a confounder must be. It is rarely done.")
FIRST, SECOND, THIRD, FOURTH = (
    "In analyses of observational studies, the measured confounders are adjusted.",
    "Quantitative techniques are used infrequently.",
    "A sensitivity analysis asks how strong a confounder must be.",
    "It is rarely done.",
)


@pytest.fixture
def session():
    reading = Session()
    reading.load(TEXT)
    return reading


# --- a drag over the term ------------------------------------------------------------------------


def test_a_drag_over_a_term_makes_its_card_with_its_sentence(session):
    _, card = session.add_definition("observational studies", sentences=(0, 0))
    assert (card.front, card.back) == ("observational studies", FIRST)
    assert card.back_html.startswith("In analyses of <b>observational studies</b>,")


def test_a_term_across_two_sentences_takes_both(session):
    _, card = session.add_definition("infrequently. A sensitivity", sentences=(1, 2))
    assert card.back == SECOND + "\n\n" + THIRD   # a paragraph break between them, as in the text


def test_the_route_takes_the_sentence_of_the_drag():
    client = create_app().test_client()
    client.post("/api/text", json={"text": TEXT})
    state = client.post("/api/definition", json={"term": "sensitivity analysis", "sentence": 2}).get_json()
    card = state["cards"][0]
    assert (card["front"], card["back"]) == ("sensitivity analysis", THIRD)
    assert client.post("/api/definition", json={"term": "x", "sentence": 99}).status_code == 400
    assert client.post("/api/definition", json={"term": "x", "sentence": 0, "last": "1"}).status_code == 400


# --- a card open in Edit ---------------------------------------------------------------------------


def test_the_card_open_in_edit_is_known_until_closed_or_forgotten(session):
    _, card = session.add_definition("observational studies", sentences=(0, 0))
    session.set_editing(card.id, now=100.0)
    assert session.editing_card(now=101.0) == card.id and session.chosen_card == card.id
    assert session.editing_card(now=100.0 + 181) is None   # a page closed while editing is not waited for
    session.set_editing(card.id, now=300.0)
    session.set_editing(None)
    assert session.editing_card(now=301.0) is None


def test_text_from_a_web_page_waits_for_the_editor_as_whole_sentences(session):
    _, card = session.add_definition("observational studies", sentences=(0, 0))
    session.set_editing(card.id, now=0.0)
    sent = session.send_to_editor("techniques are used", "Quantitative ", " infrequently. Next.", now=1.0)
    assert sent == SECOND and session.deck.inbox == [{"id": 1, "card": card.id, "text": SECOND}]
    session.take_from_inbox([1])
    assert session.deck.inbox == []
    with pytest.raises(Problem, match="No card is open"):
        session.send_to_editor("x", now=500.0)


def test_closing_edit_drops_what_was_not_taken(session):
    _, card = session.add_definition("observational studies", sentences=(0, 0))
    session.set_editing(card.id)
    session.send_to_editor("Quantitative techniques are used infrequently.")
    session.set_editing(None)
    assert session.deck.inbox == []


def test_the_routes(tmp_path):
    client = create_app().test_client()
    client.post("/api/text", json={"text": TEXT})
    card = client.post("/api/definition", json={"term": "sensitivity analysis", "sentence": 2}).get_json()["cards"][0]
    assert client.put("/api/editing", json={"card": card["id"]}).get_json()["editing"] == card["id"]
    before = client.get("/api/version").get_json()["deck"]
    state = client.post("/clip/api/text", json={"text": "rarely", "before": "It is ", "after": " done."}).get_json()
    assert "card you are editing" in state["message"] and state["count"] == 1 and state["paragraphs"] == []   # no clip, no card
    assert state["inbox"] == [{"id": 1, "card": card["id"], "text": FOURTH}]
    assert client.get("/api/version").get_json()["deck"] != before   # the editing page notices
    client.post("/api/inbox/taken", json={"ids": [1]})
    assert client.get("/api/state").get_json()["inbox"] == []
    assert client.put("/api/editing", json={"card": None}).get_json()["editing"] is None
    assert client.post("/clip/api/text", json={"text": "rarely", "before": "It is ", "after": " done."}).get_json()["count"] == 2
    assert client.put("/api/editing", json={"card": "1"}).status_code == 400
    assert client.put("/api/editing", json={"card": 99}).status_code == 400

"""A drag over a term makes its card at once with its sentence; Add sentences changes the passage by clicking
sentences of the text the card came from."""

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
    assert card.sentences == [0]


def test_a_term_across_two_sentences_takes_both(session):
    _, card = session.add_definition("infrequently. A sensitivity", sentences=(1, 2))
    assert card.back == SECOND + "\n\n" + THIRD   # a paragraph break between them, as in the text


def test_the_route_takes_the_sentence_of_the_drag():
    client = create_app().test_client()
    client.post("/api/text", json={"text": TEXT})
    state = client.post("/api/definition", json={"term": "sensitivity analysis", "sentence": 2}).get_json()
    card = state["cards"][0]
    assert (card["front"], card["back"], card["sentences"]) == ("sensitivity analysis", THIRD, [2])
    assert client.post("/api/definition", json={"term": "x", "sentence": 99}).status_code == 400
    assert client.post("/api/definition", json={"term": "x", "sentence": 0, "last": "1"}).status_code == 400


# --- Add sentences -------------------------------------------------------------------------------


def test_a_clicked_sentence_joins_the_passage_in_reading_order(session):
    _, card = session.add_definition("sensitivity analysis", sentences=(2, 2))
    _, added = session.toggle_sentence(card.id, 0)
    assert added and card.back == FIRST + "\n\n" + THIRD and card.sentences == [0, 2]
    session.toggle_sentence(card.id, 3)
    assert card.back == FIRST + "\n\n" + THIRD + " " + FOURTH


def test_a_sentence_in_the_passage_is_taken_out_again(session):
    _, card = session.add_definition("sensitivity analysis", sentences=(2, 3))
    _, added = session.toggle_sentence(card.id, 3)
    assert not added and card.back == THIRD and card.sentences == [2]
    with pytest.raises(Problem, match="at least one sentence"):
        session.toggle_sentence(card.id, 2)


def test_a_word_card_keeps_its_meaning_and_pictures_when_a_sentence_is_added(session):
    _, card = session.pick_word(*place_of(session, "infrequently"))
    session.suggest(card.id, lambda word, sentence: "Not often.")
    session.add_picture(card.id, b"\x89PNG\r\n\x1a\nx")
    name = card.pictures[0][0]
    session.toggle_sentence(card.id, 0)
    assert card.back == f"{FIRST} {SECOND}\n\nNot often.\n[[picture:{name}]]"


def test_after_an_edit_a_sentence_is_added_at_the_end_and_none_taken_out(session):
    _, card = session.add_definition("observational studies", sentences=(0, 0))
    session.edit(card.id, card.front, "My own words about it.")
    session.toggle_sentence(card.id, 1)
    assert card.back == "My own words about it.\n\n" + SECOND
    with pytest.raises(Problem, match="with Edit"):
        session.toggle_sentence(card.id, 1)


def test_only_the_text_the_card_came_from(tmp_path):
    client = create_app().test_client()
    client.post("/api/text", json={"text": TEXT})
    card = client.post("/api/definition", json={"term": "sensitivity analysis", "sentence": 2}).get_json()["cards"][0]
    client.post("/clip/api/text", json={"text": "A clip from the web. Second sentence."})
    response = client.put(f"/clip/api/cards/{card['id']}/sentences", json={"sentence": 0})
    assert response.status_code == 400 and "in Read" in response.get_json()["error"]
    state = client.put(f"/api/cards/{card['id']}/sentences", json={"sentence": 3}).get_json()
    assert state["cards"][0]["back"] == THIRD + " " + FOURTH and "Sentence added" in state["message"]


def test_a_clip_removed_before_the_card_moves_its_sentence_numbers():
    clips = Session(name="clip")
    clips.add("An earlier clip. With two sentences.")
    clips.add("Outliers can skew the mean. The median resists them.")
    _, card = clips.pick_word(*place_of(clips, "skew"))
    assert card.sentences == [2]
    clips.remove_clip(0)
    assert card.sentences == [0]
    clips.toggle_sentence(card.id, 1)
    assert card.back == "Outliers can skew the mean. The median resists them."


def test_a_card_whose_clip_is_gone_cannot_add_sentences():
    clips = Session(name="clip")
    clips.add("Outliers can skew the mean.")
    _, card = clips.pick_word(*place_of(clips, "skew"))
    clips.remove_clip(0)
    clips.add("Another clip.")
    with pytest.raises(Problem, match="not here any more"):
        clips.toggle_sentence(card.id, 0)

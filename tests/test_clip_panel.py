"""clip-panel: clips from web pages go to a session of their own, beside the text in Read."""

import pytest
from reading_helper import place_of

from sentmine.app import create_app
from sentmine.memory import CardMemory
from sentmine.reading import Problem, Session

SENTENCE = "Outliers can skew the mean considerably."
DEFINITION = "A confounder is a variable that influences both the treatment and the outcome."


@pytest.fixture
def client(tmp_path):
    return create_app(Session(CardMemory(tmp_path / "cards.db"))).test_client()


def clip(client, text, kind="word"):
    response = client.post("/clip/api/text", json={"text": text, "kind": kind})
    assert response.status_code == 200, response.get_json()
    return response.get_json()


def click(client, state, word, prefix="/clip"):
    sentence, number = place_of(state["paragraphs"], word)
    return client.post(prefix + "/api/word", json={"sentence": sentence, "word": number}).get_json()


def text_of(state):
    return " ".join(piece["text"] for p in state["paragraphs"] for s in p for piece in s["pieces"] if "word" in piece)


def test_a_clip_adds_after_the_earlier_ones_and_keeps_their_cards(client):
    state = click(client, clip(client, SENTENCE), "skew")
    assert state["count"] == 1
    state = clip(client, "Its variance was large.")
    assert len(state["paragraphs"]) == 2 and state["count"] == 1
    assert state["clip_kinds"] == ["word", "word"]


def test_read_is_never_touched_by_a_clip(client):
    read = client.post("/api/text", json={"text": "The median resists outliers."}).get_json()
    click(client, read, "median", prefix="")
    clip(client, SENTENCE)
    after = client.get("/api/state").get_json()
    assert "median" in text_of(after) and "skew" not in text_of(after)
    assert after["count"] == 1 and after["clip_kinds"] is None


def test_a_definition_clip_is_one_paragraph_and_its_drag_makes_the_card(client):
    state = clip(client, "A confounder is a variable\n\nthat influences both the treatment and the outcome.", "definition")
    assert len(state["paragraphs"]) == 1 and state["clip_kinds"] == ["definition"]
    state = client.post("/clip/api/definition", json={"term": "confounder", "passage": DEFINITION}).get_json()
    assert state["count"] == 1 and state["cards"][0]["front"].startswith("confounder")


def test_clip_cards_can_be_edited_downloaded_and_deleted_under_clip(client):
    state = click(client, clip(client, SENTENCE), "skew")
    card_id = state["cards"][0]["id"]
    assert client.put(f"/clip/api/cards/{card_id}", json={"front": "f", "back": "b"}).status_code == 200
    assert client.get("/clip/api/deck?name=web").status_code == 200
    assert client.delete(f"/clip/api/cards/{card_id}").get_json()["count"] == 0


def test_the_clip_page_holds_the_clips(client):
    clip(client, SENTENCE)
    page = client.get("/clip")
    assert page.status_code == 200 and b"Outliers" in page.data


@pytest.mark.parametrize("text, kind", [("   ", "word"), ("A sentence.", "poem")])
def test_a_clip_without_text_or_with_another_kind_is_refused(text, kind):
    with pytest.raises(Problem):
        Session().add(text, kind)

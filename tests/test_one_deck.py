"""one-deck: the cards from the text in Read and from web pages are one deck, shown in both places."""

import io

import pytest
from pdf_helper import make_pdf
from reading_helper import place_of

from sentmine.app import create_app
from sentmine.memory import CardMemory
from sentmine.reading import Session


@pytest.fixture
def client(tmp_path):
    return create_app(Session(CardMemory(tmp_path / "cards.db"))).test_client()


def click(client, prefix, word):
    state = client.get(prefix + "/api/state").get_json()
    sentence, number = place_of(state["paragraphs"], word)
    return client.post(prefix + "/api/word", json={"sentence": sentence, "word": number}).get_json()


def picked(state):
    return [p["text"] for par in state["paragraphs"] for s in par for p in s["pieces"] if p.get("picked")]


def read_pdf(client, sentences):
    data = make_pdf([sentences])
    return client.post("/api/file", data={"file": (io.BytesIO(data), "primer.pdf")}, content_type="multipart/form-data")


def test_cards_from_read_and_the_web_are_one_deck_in_both_places(client):
    read_pdf(client, ["Outliers can skew the mean considerably."])
    click(client, "", "skew")
    client.post("/clip/api/text", json={"text": "Salami is a cured sausage.", "kind": "word"})
    click(client, "/clip", "cured")
    read, clip = client.get("/api/state").get_json(), client.get("/clip/api/state").get_json()
    assert [c["back"] for c in read["cards"]] == [c["back"] for c in clip["cards"]] == ["skew", "cured (cure)"]
    assert [c["origin"] for c in read["cards"]] == ["primer.pdf, p. 1", "a web page"]
    assert read["count_text"] == clip["count_text"] == "2 cards"


def test_each_text_marks_only_its_own_cards(client):
    client.post("/api/text", json={"text": "The data were cured of errors."})
    client.post("/clip/api/text", json={"text": "Salami is a cured sausage.", "kind": "word"})
    click(client, "/clip", "cured")
    assert picked(client.get("/clip/api/state").get_json()) == ["cured"]
    assert picked(client.get("/api/state").get_json()) == []
    state = click(client, "", "cured")   # the same word in Read: the deck already has it
    assert state["result"] == "duplicate" and state["count"] == 1


def test_a_new_text_in_read_keeps_the_cards_from_web_pages(client):
    client.post("/api/text", json={"text": "Outliers can skew the mean."})
    click(client, "", "skew")
    client.post("/clip/api/text", json={"text": "Salami is a cured sausage.", "kind": "word"})
    click(client, "/clip", "cured")
    state = client.post("/api/text", json={"text": "A completely different text."}).get_json()
    assert [c["back"] for c in state["cards"]] == ["cured (cure)"]


def test_a_web_picture_can_go_to_a_card_from_the_pdf(client):
    read_pdf(client, ["Outliers can skew the mean considerably."])
    card = click(client, "", "skew")["cards"][-1]
    client.post("/clip/api/text", json={"text": "Salami is a cured sausage.", "kind": "word"})
    click(client, "/clip", "cured")
    assert client.put(f"/clip/api/cards/{card['id']}/chosen").get_json()["chosen_card"] == card["id"]
    import base64
    png = b"\x89PNG\r\n\x1a\n" + b"x"
    state = client.post(f"/clip/api/cards/{card['id']}/pictures", json={"png": base64.b64encode(png).decode()}).get_json()
    assert len(next(c for c in state["cards"] if c["id"] == card["id"])["pictures"]) == 1


def test_sending_remembers_each_card_with_the_text_it_came_from(client, tmp_path):
    client.post("/api/text", json={"text": "Outliers can skew the mean."})
    click(client, "", "skew")
    client.post("/clip/api/text", json={"text": "Salami is a cured sausage.", "kind": "word"})
    click(client, "/clip", "cured")
    assert client.get("/api/deck?name=both").status_code == 200
    memory_cards = client.get("/api/memory").get_json()["cards"]
    assert sorted(c["back_html"] for c in memory_cards) == ["cured (cure)", "skew"]


def test_pictures_go_here_works_from_read_too(client):
    client.post("/api/text", json={"text": "Outliers can skew the mean."})
    first = click(client, "", "skew")["cards"][-1]
    click(client, "", "mean")
    state = client.put(f"/api/cards/{first['id']}/chosen")
    assert state.status_code == 200 and state.get_json()["chosen_card"] == first["id"]
    assert client.get("/clip/api/state").get_json()["chosen_card"] == first["id"]   # one choice, both views

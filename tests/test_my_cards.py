"""memory-database: the My cards page and its API."""

from datetime import date

import pytest
from reading_helper import place_of

from sentmine.app import create_app
from sentmine.history import Entry
from sentmine.memory import CardMemory
from sentmine.reading import Session

SKEW = Entry("word", "skew", "Outliers can skew it considerably.", "skew", "skew", "2026-10-09")
SIGHED = Entry("word", "sigh", "Its owner sighed.", "sighed (sigh)", "sighed", "2026-10-17")
SD = Entry("definition", "standard deviation", "standard deviation", "How <spread> out.", "", "2026-10-22")


@pytest.fixture
def memory(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    memory.add([SKEW, SIGHED, SD])
    return memory


@pytest.fixture
def client(memory):
    return create_app(Session(memory)).test_client()


def test_the_page_is_served_and_linked_both_ways(client):
    page = client.get("/cards")
    assert page.status_code == 200 and page.mimetype == "text/html"
    assert b'href="/"' in page.data
    assert b'href="/cards"' in client.get("/").data


def test_the_cards_come_newest_first_with_their_dates(client):
    data = client.get("/api/memory").get_json()
    assert [card["date"] for card in data["cards"]] == ["2026-10-22", "2026-10-17", "2026-10-09"]
    assert (data["total"], data["total_text"], data["memory_warning"]) == (3, "3 cards", "")
    word = data["cards"][2]
    assert (word["kind"], word["front_html"], word["back_html"]) == ("word", "Outliers can <b>skew</b> it considerably.", "skew")
    assert data["cards"][0]["back_html"] == "How &lt;spread&gt; out."  # escaped for the page


def test_searching(client):
    data = client.get("/api/memory?q=dev").get_json()
    assert [card["front_html"] for card in data["cards"]] == ["standard deviation"]
    assert data["total"] == 1


def test_progress_comes_with_the_list(client, monkeypatch):
    progress = client.get("/api/memory").get_json()["progress"]
    assert (progress["total"], progress["words"], progress["definitions"]) == (3, 2, 1)
    assert len(progress["months"]) == 6


def test_deleting_means_no_earlier_card_afterwards(client):
    skew_id = next(card["id"] for card in client.get("/api/memory?q=skew").get_json()["cards"])
    data = client.delete(f"/api/memory/{skew_id}").get_json()
    assert data["total"] == 2
    client.post("/api/text", json={"text": "Polls skew young."})
    sentence, word = place_of(client.get("/api/state").get_json()["paragraphs"], "skew")
    state = client.post("/api/word", json={"sentence": sentence, "word": word}).get_json()
    assert state["result"] == "added"  # made straight away, no earlier card shown


def test_deleting_a_card_that_is_gone_is_a_400(client):
    assert client.delete("/api/memory/999").status_code == 400


def test_a_damaged_database_shows_the_reason_and_no_cards(tmp_path):
    path = tmp_path / "cards.db"
    path.write_bytes(b"not a database " * 50)
    data = create_app(Session(CardMemory(path))).test_client().get("/api/memory").get_json()
    assert "could not be opened" in data["memory_warning"]
    assert (data["cards"], data["total"]) == ([], 0)


def test_an_app_without_a_memory_says_so():
    client = create_app().test_client()
    data = client.get("/api/memory").get_json()
    assert (data["cards"], data["total"]) == ([], 0) and "no card memory" in data["memory_warning"]
    assert client.delete("/api/memory/1").status_code == 400

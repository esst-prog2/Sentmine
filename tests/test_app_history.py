"""remember-cards in the web app: the earlier card in the state, making it anyway, remembering on download."""

from urllib.parse import unquote

import pytest
from reading_helper import place_of

from sentmine import app as app_module
from sentmine.app import create_app
from sentmine.history import Entry
from sentmine.memory import CardMemory
from sentmine.reading import Session

SKEW_9_OCT = Entry("word", "skew", "Outliers can skew it considerably.", "skew", "skew", "2026-10-09")


@pytest.fixture
def history(tmp_path):
    return CardMemory(tmp_path / "cards.db")


def client_with(history, text):
    client = create_app(Session(history)).test_client()
    client.post("/api/text", json={"text": text})
    return client


def click_body(client, word, **extra):
    sentence, number = place_of(client.get("/api/state").get_json()["paragraphs"], word)
    return {"sentence": sentence, "word": number, **extra}


def test_the_earlier_card_comes_with_the_state(history):
    history.add([SKEW_9_OCT])
    client = client_with(history, "Polls skewed young.")
    state = client.post("/api/word", json=click_body(client, "skewed")).get_json()
    assert state["result"] == "earlier"
    assert state["cards"] == []
    assert state["earlier"] == {
        "kind": "word",
        "front_html": "Outliers can <b>skew</b> it considerably.",
        "back_html": "skew",
        "date": "2026-10-09",
    }
    assert "already has a card from 2026-10-09" in state["message"]


def test_making_it_anyway_shows_the_earlier_date_in_the_preview(history):
    history.add([SKEW_9_OCT])
    client = client_with(history, "Polls skewed young.")
    state = client.post("/api/word", json=click_body(client, "skewed", anyway=True)).get_json()
    assert state["result"] == "added"
    assert state["earlier"] is None
    assert state["cards"][0]["earlier"] == "2026-10-09"
    assert state["cards"][0]["back"] == "skewed (skew)"


def test_a_definition_made_anyway(history):
    history.add([Entry("definition", "variance", "variance", "Spread.", "", "2026-10-09")])
    client = client_with(history, "Some notes.")
    state = client.post("/api/definition", json={"term": "Variance", "passage": "Spread."}).get_json()
    assert state["result"] == "earlier"
    state = client.post("/api/definition", json={"term": "Variance", "passage": "Spread.", "anyway": True}).get_json()
    assert state["cards"][0]["earlier"] == "2026-10-09"


@pytest.mark.parametrize("value", ["yes", 1, None])
def test_anyway_must_be_true_or_false(history, value):
    client = client_with(history, "Polls skewed young.")
    response = client.post("/api/word", json=click_body(client, "skewed", anyway=value))
    assert response.status_code == 400


def test_the_download_remembers_the_cards(history):
    client = client_with(history, "Its owner sighed.")
    client.post("/api/word", json=click_body(client, "sighed"))
    response = client.get("/api/deck?name=new")
    assert response.status_code == 200
    assert "X-Sentmine-Warning" not in response.headers
    assert [entry.back for entry in CardMemory(history.path).entries] == ["sighed (sigh)"]


def test_a_new_session_finds_the_card_downloaded_in_an_earlier_one(history):
    first = client_with(history, "Its owner sighed.")
    first.post("/api/word", json=click_body(first, "sighed"))
    first.get("/api/deck?name=new")
    later = client_with(CardMemory(history.path), "A long sigh.")  # the app started again
    state = later.post("/api/word", json=click_body(later, "sigh")).get_json()
    assert state["result"] == "earlier"


def test_a_damaged_history_is_shown_and_the_deck_still_downloads(tmp_path):
    path = tmp_path / "cards.db"
    path.write_text("damaged\n", encoding="utf-8")
    client = client_with(CardMemory(path), "Its owner sighed.")
    assert "could not be opened" in client.get("/api/state").get_json()["memory_warning"]
    client.post("/api/word", json=click_body(client, "sighed"))
    response = client.get("/api/deck?name=new")
    assert response.status_code == 200 and len(response.data) > 0
    assert "not remembered" in unquote(response.headers["X-Sentmine-Warning"])
    assert path.read_text(encoding="utf-8") == "damaged\n"


def test_without_a_history_there_is_no_warning():
    state = create_app().test_client().get("/api/state").get_json()
    assert state["memory_warning"] == "" and state["earlier"] is None


def test_the_real_command_opens_the_history_named_by_the_environment(monkeypatch, tmp_path):
    path = tmp_path / "mine.db"
    monkeypatch.setenv("SENTMINE_DATABASE", str(path))
    started = {}

    class FakeApp:
        def run(self, host, port):
            started["run"] = (host, port)

    def fake_create_app(session):
        started["memory"] = session.memory
        return FakeApp()

    monkeypatch.setattr(app_module, "create_app", fake_create_app)
    monkeypatch.setattr(app_module, "free_port", lambda: 8123)
    assert app_module.serve(open_browser=False) == 0
    assert started["memory"].path == path
    assert started["run"] == ("127.0.0.1", 8123)

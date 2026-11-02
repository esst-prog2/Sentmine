"""ai-meanings. No test here touches the network: answers are invented by hand and passed in."""

import io
import urllib.error

import pytest
from reading_helper import place_of

from sentmine import app as app_module
from sentmine import meaning as meaning_module
from sentmine.app import create_app
from sentmine.meaning import MODEL, MeaningProblem, find_api_key, suggest_meaning
from sentmine.memory import CardMemory
from sentmine.reading import Problem, Session

SKEW_SENTENCE = "Outliers can skew it considerably."
MEANING = "To make something less accurate."


def fake_ask(word, sentence):
    return MEANING


def reply(text):
    return {"choices": [{"message": {"content": text}}]}


@pytest.fixture
def session():
    reading = Session()
    reading.load("Its owner sighed. " + SKEW_SENTENCE + " Some more text here.")
    return reading


# --- the request ------------------------------------------------------------------------


def test_only_the_word_and_the_sentence_are_sent():
    sent = {}

    def post(body, key):
        sent.update(body=body, key=key)
        return reply(MEANING)

    assert suggest_meaning("skew", SKEW_SENTENCE, "test-key", post) == MEANING
    assert sent["key"] == "test-key"
    assert sent["body"]["model"] == MODEL == "gpt-5-nano"
    text = sent["body"]["messages"][0]["content"]
    assert "Word: skew" in text and SKEW_SENTENCE in text
    assert "Some more text" not in text


def test_the_answer_is_trimmed():
    assert suggest_meaning("skew", SKEW_SENTENCE, "k", lambda body, key: reply("  A meaning.\n")) == "A meaning."


@pytest.mark.parametrize("answer", [reply(""), reply("   "), reply(None), {"choices": []}, {}])
def test_an_empty_answer_is_a_problem(answer):
    with pytest.raises(MeaningProblem, match="no meaning"):
        suggest_meaning("skew", SKEW_SENTENCE, "k", lambda body, key: answer)


def http_error(code):
    return urllib.error.HTTPError("https://api.openai.com", code, "error", {}, io.BytesIO(b"{}"))


@pytest.mark.parametrize(
    "failure, words",
    [
        (http_error(401), "refused the API key"),
        (http_error(429), "no credit"),
        (http_error(500), "error \\(500\\)"),
        (urllib.error.URLError("no route"), "could not be reached"),
        (TimeoutError(), "could not be reached"),
    ],
)
def test_each_failure_is_said_in_plain_words(monkeypatch, failure, words):
    def fail(request, timeout):
        raise failure

    monkeypatch.setattr(meaning_module.urllib.request, "urlopen", fail)
    with pytest.raises(MeaningProblem, match=words):
        suggest_meaning("skew", SKEW_SENTENCE, "k")


# --- the key ---------------------------------------------------------------------------


def test_the_variable_comes_first(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "from-variable")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert find_api_key() == "from-variable"


def test_the_file_in_the_user_folder(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path))
    (tmp_path / "sentmine").mkdir()
    (tmp_path / "sentmine" / ".env").write_text("# a comment\nOPENAI_API_KEY= from-file \n", encoding="utf-8")
    assert find_api_key() == "from-file"


def test_no_key_anywhere(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert find_api_key() == ""


# --- the session ------------------------------------------------------------------------


def test_the_meaning_goes_under_the_word(session):
    _, card = session.pick_word(*place_of(session, "skew"))
    session.suggest(card.id, fake_ask)
    assert card.back == "skew\n" + MEANING
    assert card.back_html == "skew<br>" + MEANING


def test_the_ask_gets_the_word_and_the_card_sentence(session):
    _, card = session.pick_word(*place_of(session, "skew"))
    asked = []
    session.suggest(card.id, lambda word, sentence: asked.append((word, sentence)) or MEANING)
    assert asked == [("skew", SKEW_SENTENCE)]


def test_the_base_form_stays_on_the_first_line(session):
    _, card = session.pick_word(*place_of(session, "sighed"))
    session.suggest(card.id, fake_ask)
    assert card.back == "sighed (sigh)\n" + MEANING


def test_pressing_again_replaces_the_meaning(session):
    _, card = session.pick_word(*place_of(session, "skew"))
    session.suggest(card.id, fake_ask)
    session.suggest(card.id, lambda word, sentence: "A second try.")
    assert card.back == "skew\nA second try."


def test_a_definition_card_gets_no_meaning(session):
    _, card = session.add_definition("variance", "How spread out values are.")
    with pytest.raises(Problem, match="word cards"):
        session.suggest(card.id, fake_ask)
    assert card.back == "How spread out values are."


def test_a_failed_request_leaves_the_card_as_it_was(session):
    _, card = session.pick_word(*place_of(session, "skew"))

    def fails(word, sentence):
        raise MeaningProblem("OpenAI could not be reached.")

    with pytest.raises(MeaningProblem):
        session.suggest(card.id, fails)
    assert card.back == "skew"


def test_an_edited_meaning_is_what_is_remembered(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    reading = Session(memory)
    reading.load(SKEW_SENTENCE)
    _, card = reading.pick_word(*place_of(reading, "skew"))
    reading.suggest(card.id, fake_ask)
    reading.edit(card.id, card.front, "skew\nMy own words.")
    reading.export(tmp_path / "new.apkg", day="2026-11-02")
    assert memory.entries[0].back == "skew\nMy own words."


# --- the app -----------------------------------------------------------------------------


def client_with_card(ask=fake_ask):
    client = create_app(ask=ask).test_client()
    client.post("/api/text", json={"text": SKEW_SENTENCE})
    sentence, word = place_of(client.get("/api/state").get_json()["paragraphs"], "skew")
    state = client.post("/api/word", json={"sentence": sentence, "word": word}).get_json()
    return client, state["cards"][0]["id"]


def test_the_button_route_fills_the_back():
    client, card_id = client_with_card()
    state = client.post(f"/api/cards/{card_id}/meaning").get_json()
    assert state["can_suggest"] is True
    assert state["cards"][0]["back_html"] == "skew<br>" + MEANING


def test_without_a_key_there_is_no_button_and_the_route_refuses():
    client = create_app().test_client()
    assert client.get("/api/state").get_json()["can_suggest"] is False
    assert client.post("/api/cards/1/meaning").status_code == 400


def test_a_failure_comes_back_as_a_message_and_the_card_is_unchanged():
    def fails(word, sentence):
        raise MeaningProblem("OpenAI refused the API key.")

    client, card_id = client_with_card(fails)
    response = client.post(f"/api/cards/{card_id}/meaning")
    assert response.status_code == 400 and "refused" in response.get_json()["error"]
    assert client.get("/api/state").get_json()["cards"][0]["back"] == "skew"


def test_the_key_never_reaches_the_page(monkeypatch, tmp_path):
    client = create_app(ask=fake_ask).test_client()
    assert b"sk-" not in client.get("/api/state").data


@pytest.mark.parametrize("key, shown", [("sk-secret-value", "AI meanings: on"), ("", "AI meanings: off")])
def test_the_command_says_whether_meanings_are_on_and_never_prints_the_key(monkeypatch, tmp_path, capsys, key, shown):
    monkeypatch.setenv("SENTMINE_DATABASE", str(tmp_path / "cards.db"))
    monkeypatch.setattr(app_module, "find_api_key", lambda: key)
    monkeypatch.setattr(app_module, "free_port", lambda: 8123)
    started = {}

    class FakeApp:
        def run(self, host, port):
            pass

    monkeypatch.setattr(app_module, "create_app", lambda session, ask: started.update(ask=ask) or FakeApp())
    app_module.serve(open_browser=False)
    out = capsys.readouterr().out
    assert shown in out and "sk-secret-value" not in out
    assert (started["ask"] is not None) == bool(key)

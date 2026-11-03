"""send-to-anki. A fake AnkiConnect stands in for Anki; no test needs Anki or the network."""

import io
import re
import urllib.error

import pytest
from reading_helper import place_of

from sentmine import anki
from sentmine.anki import AnkiProblem, send_notes
from sentmine.app import create_app
from sentmine.deck import MODEL
from sentmine.memory import CardMemory
from sentmine.reading import Problem, Session

TEXT = "Polls skew young. Outliers can distort it. The median resists outliers."
NOTES = [("one <b>a</b>", "a"), ("two <b>b</b>", "b"), ("three <b>c</b>", "c")]


class FakeAnki:
    """Answers AnkiConnect's requests the way AnkiConnect does, keeping notes in memory.

    Like Anki, it calls a note a duplicate when its front without HTML matches another in the deck,
    unless the note allows duplicates.
    """

    def __init__(self, version=6, note_types=(MODEL.name,), notes=()):
        self.version = version
        self.note_types = list(note_types)
        self.decks = {}
        for deck, front in notes:
            self.decks.setdefault(deck, []).append(front)
        self.actions = []
        self.created = None
        self.queries = []

    def __call__(self, body):
        action, params = body["action"], body.get("params", {})
        self.actions.append(action)
        assert body["version"] == 6
        if action == "version":
            return {"result": self.version, "error": None}
        if action == "modelNames":
            return {"result": list(self.note_types), "error": None}
        if action == "createModel":
            self.created = params
            self.note_types.append(params["modelName"])
            return {"result": {}, "error": None}
        if action == "createDeck":
            self.decks.setdefault(params["deck"], [])
            return {"result": 1, "error": None}
        if action == "findNotes":
            self.queries.append(params["query"])
            deck = re.match(r'"deck:([^"]*)"', params["query"]).group(1)
            return {"result": [[deck, n] for n in range(len(self.decks.get(deck, [])))], "error": None}
        if action == "notesInfo":
            return {"result": [{"fields": {"Front": {"value": self.decks[d][n]}}} for d, n in params["notes"]],
                    "error": None}
        if action == "addNotes":
            errors = [self._refusal(note) for note in params["notes"]]
            if any(errors):  # AnkiConnect adds nothing and lists the reasons
                return {"result": None, "error": [e for e in errors if e]}
            for note in params["notes"]:
                self.decks[note["deckName"]].append(note["fields"]["Front"])
            return {"result": list(range(len(params["notes"]))), "error": None}
        return {"result": None, "error": "unsupported action"}

    def _refusal(self, note):
        if note["modelName"] not in self.note_types:
            return "model was not found: " + note["modelName"]
        if note["options"].get("allowDuplicate"):
            return None
        plain = re.sub("<[^>]*>", "", note["fields"]["Front"])
        if plain in [re.sub("<[^>]*>", "", front) for front in self.decks.get(note["deckName"], [])]:
            return "cannot create note because it is a duplicate"
        return None


# --- talking to AnkiConnect --------------------------------------------------------------------


def test_three_cards_are_added_in_order():
    fake = FakeAnki()
    assert send_notes(NOTES, "stats", fake) == (3, 0)
    assert fake.decks["stats"] == ["one <b>a</b>", "two <b>b</b>", "three <b>c</b>"]
    assert "createModel" not in fake.actions


def test_a_missing_note_type_is_made_like_the_apkg_one():
    fake = FakeAnki(note_types=["Basic"])
    send_notes(NOTES, "stats", fake)
    assert fake.created["modelName"] == MODEL.name
    assert fake.created["inOrderFields"] == ["Front", "Back"]
    assert fake.created["cardTemplates"][0]["Front"] == "{{Front}}"
    assert fake.actions.index("createModel") < fake.actions.index("addNotes")


def test_a_card_already_in_the_deck_is_skipped_and_the_rest_added():
    fake = FakeAnki(notes=[("stats", "one <b>a</b>")])
    assert send_notes(NOTES, "stats", fake) == (2, 1)
    assert fake.decks["stats"].count("one <b>a</b>") == 1


def test_the_same_card_in_another_deck_is_not_a_duplicate():
    fake = FakeAnki(notes=[("other", "one <b>a</b>")])
    assert send_notes(NOTES, "stats", fake) == (3, 0)


def test_all_cards_already_there_adds_nothing():
    fake = FakeAnki(notes=[("stats", front) for front, _ in NOTES])
    assert send_notes(NOTES, "stats", fake) == (0, 3)
    assert "addNotes" not in fake.actions


def test_an_old_ankiconnect_is_refused_before_anything_is_changed():
    fake = FakeAnki(version=5)
    with pytest.raises(AnkiProblem, match="too old"):
        send_notes(NOTES, "stats", fake)
    assert fake.actions == ["version"]


def test_two_cards_from_one_sentence_are_both_added():
    """Anki compares fronts without HTML; the bold word is what tells these two cards apart."""
    fake = FakeAnki()
    notes = [("State <b>Management</b>: text.", "management"), ("<b>State</b> Management: text.", "state")]
    assert send_notes(notes, "stats", fake) == (2, 0)
    assert len(fake.decks["stats"]) == 2


def test_a_card_from_the_same_sentence_already_there_does_not_block_another_word():
    fake = FakeAnki(notes=[("stats", "<b>State</b> Management: text.")])
    assert send_notes([("State <b>Management</b>: text.", "management")], "stats", fake) == (1, 0)


def test_only_the_named_deck_is_searched_without_its_subdecks():
    fake = FakeAnki()
    send_notes(NOTES, "stats", fake)
    assert fake.queries == [f'"deck:stats" -"deck:stats::*" "note:{MODEL.name}"']


def test_ankis_reasons_are_said_once_each():
    fake = FakeAnki()
    fake.note_types = [MODEL.name]
    fake._refusal = lambda note: "the field Front is empty"
    with pytest.raises(AnkiProblem) as caught:
        send_notes(NOTES, "stats", fake)
    assert str(caught.value) == "Anki refused the cards: the field Front is empty"


def test_an_answer_that_is_not_ankiconnects_is_a_problem():
    with pytest.raises(AnkiProblem, match="does not understand"):
        send_notes(NOTES, "stats", lambda body: {"something": "else"})


def test_a_notes_answer_of_the_wrong_shape_is_a_problem():
    def odd(body):
        if body["action"] == "notesInfo":
            return {"result": [{"no fields": True}], "error": None}
        return FakeAnki(notes=[("stats", "old")])(body)

    with pytest.raises(AnkiProblem, match="does not understand"):
        send_notes(NOTES, "stats", odd)


@pytest.mark.parametrize(
    "failure", [urllib.error.URLError("refused"), ConnectionResetError(), TimeoutError()]
)
def test_anki_not_open_is_said_in_plain_words(monkeypatch, failure):
    def fail(request, timeout):
        raise failure

    monkeypatch.setattr(anki.urllib.request, "urlopen", fail)
    with pytest.raises(AnkiProblem, match="Open Anki") as caught:
        send_notes(NOTES, "stats")
    assert "2055492159" in str(caught.value)


def test_requests_go_to_this_computer_only(monkeypatch):
    seen = []

    def answer(request, timeout):
        seen.append(request.full_url)
        return io.BytesIO(b'{"result": 6, "error": null}')

    monkeypatch.setattr(anki.urllib.request, "urlopen", answer)
    with pytest.raises(AnkiProblem, match="does not understand"):  # 6 is not a list of note types
        send_notes(NOTES, "stats")
    assert seen and all(url == "http://127.0.0.1:8765" for url in seen)


# --- the session ---------------------------------------------------------------------------------


def via(fake):
    """What the app passes to the session: send_notes talking to `fake`."""
    return lambda notes, deck: send_notes(notes, deck, fake)


def session_with_cards(memory=None, words=("skew", "distort")):
    reading = Session(memory)
    reading.load(TEXT)
    for word in words:
        reading.pick_word(*place_of(reading, word))
    return reading


def test_sent_cards_are_remembered(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    reading = session_with_cards(memory)
    assert reading.send("stats", via(FakeAnki()), day="2026-11-04") == (2, 0, "")
    assert {entry.word for entry in memory.entries} == {"skew", "distort"}


def test_cards_already_in_anki_are_remembered_too(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    reading = session_with_cards(memory)
    fake = FakeAnki(notes=[("stats", reading.cards[0].front_html)])
    assert reading.send("stats", via(fake), day="2026-11-04")[:2] == (1, 1)
    assert memory.count() == 2


def test_a_failed_send_remembers_nothing_and_keeps_the_cards(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    reading = session_with_cards(memory)
    with pytest.raises(AnkiProblem):
        reading.send("stats", via(FakeAnki(version=5)))
    assert memory.count() == 0 and len(reading.cards) == 2


def test_an_edited_card_is_sent_as_the_preview_shows_it():
    reading = session_with_cards(words=("skew",))
    reading.edit(reading.cards[0].id, "Edited front", "edited back")
    fake = FakeAnki()
    reading.send("stats", via(fake))
    assert fake.decks["stats"] == ["Edited front"]


def test_no_cards_sends_nothing():
    fake = FakeAnki()
    with pytest.raises(Problem, match="no cards"):
        session_with_cards(words=()).send("stats", via(fake))
    assert fake.actions == []


# --- the app -------------------------------------------------------------------------------------


def client_with_cards(fake, memory=None):
    client = create_app(Session(memory), send=via(fake)).test_client()
    client.post("/api/text", json={"text": TEXT})
    for word in ("skew", "distort"):
        sentence, number = place_of(client.get("/api/state").get_json()["paragraphs"], word)
        client.post("/api/word", json={"sentence": sentence, "word": number})
    return client


def test_the_route_sends_to_the_named_deck_and_says_how_many():
    fake = FakeAnki()
    state = client_with_cards(fake).post("/api/send", json={"deck": "stats"}).get_json()
    assert len(fake.decks["stats"]) == 2
    assert state["message"] == "Sent to the deck 'stats' in Anki: 2 cards added. Now in My cards too."
    assert state["count"] == 2


def test_the_deck_name_is_cleaned_as_for_download():
    fake = FakeAnki()
    client_with_cards(fake).post("/api/send", json={"deck": "../../evil"})
    assert list(fake.decks) == ["evil"]


def test_an_empty_deck_name_becomes_new():
    fake = FakeAnki()
    client_with_cards(fake).post("/api/send", json={"deck": "  "})
    assert list(fake.decks) == ["new"]


def test_the_message_counts_cards_already_there():
    fake = FakeAnki()
    client = client_with_cards(fake)
    client.post("/api/send", json={"deck": "stats"})
    again = client.post("/api/send", json={"deck": "stats"}).get_json()
    assert again["message"] == "All 2 cards were already in the deck 'stats' in Anki."


def test_one_already_there_is_said_in_the_singular():
    fake = FakeAnki()
    client = client_with_cards(fake)
    front = client.get("/api/state").get_json()["cards"][0]["front_html"]
    fake.decks["stats"] = [front]
    message = client.post("/api/send", json={"deck": "stats"}).get_json()["message"]
    assert "1 card added, 1 was already there" in message


def test_anki_closed_comes_back_as_a_message_and_the_cards_stay():
    def closed(notes, deck):
        raise AnkiProblem("Anki did not answer. Open Anki and try again.")

    client = create_app(send=closed).test_client()
    client.post("/api/text", json={"text": TEXT})
    sentence, number = place_of(client.get("/api/state").get_json()["paragraphs"], "skew")
    client.post("/api/word", json={"sentence": sentence, "word": number})
    response = client.post("/api/send", json={"deck": "stats"})
    assert response.status_code == 400 and "Open Anki" in response.get_json()["error"]
    assert client.get("/api/state").get_json()["count"] == 1


def test_one_card_already_there_is_said_in_the_singular():
    fake = FakeAnki()
    client = create_app(send=via(fake)).test_client()
    client.post("/api/text", json={"text": TEXT})
    sentence, number = place_of(client.get("/api/state").get_json()["paragraphs"], "skew")
    client.post("/api/word", json={"sentence": sentence, "word": number})
    client.post("/api/send", json={"deck": "stats"})
    again = client.post("/api/send", json={"deck": "stats"}).get_json()["message"]
    assert again == "The card was already in the deck 'stats' in Anki."


def test_a_request_without_a_deck_name_is_refused():
    assert client_with_cards(FakeAnki()).post("/api/send", json={}).status_code == 400

"""clip-panel: clips from web pages go to a session of their own, beside the text in Read."""

import pytest
from reading_helper import place_of, post_clip

from sentmine.app import create_app
from sentmine.memory import CardMemory
from sentmine.reading import Problem, Session

SENTENCE = "Outliers can skew the mean considerably."
DEFINITION = "A confounder is a variable that influences both the treatment and the outcome."


@pytest.fixture
def client(tmp_path):
    return create_app(Session(CardMemory(tmp_path / "cards.db"))).test_client()


def clip(client, text, **around):
    response = post_clip(client, {"text": text, **around})
    assert response.status_code == 200, response.get_json()
    return response.get_json()


def card_from(client, text, **around):
    """The right-click and the card it makes."""
    response = client.post("/clip/api/text", json={"text": text, **around})
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
    assert state["clips"] is True


def test_read_is_never_touched_by_a_clip(client):
    read = client.post("/api/text", json={"text": "The median resists outliers."}).get_json()
    click(client, read, "median", prefix="")
    clip(client, SENTENCE)
    after = client.get("/api/state").get_json()
    assert "median" in text_of(after) and "skew" not in text_of(after)
    assert after["count"] == 1 and after["clips"] is False


def test_a_clip_is_one_paragraph_and_a_drag_over_its_term_makes_the_card(client):
    state = clip(client, "A confounder is a variable\n\nthat influences both the treatment and the outcome.")
    assert len(state["paragraphs"]) == 1 and state["count"] == 0
    state = client.post("/clip/api/definition", json={"term": "confounder", "passage": DEFINITION}).get_json()
    assert state["count"] == 1 and (state["cards"][0]["front"], state["cards"][0]["back"]) == ("confounder", DEFINITION)


# --- one right-click: its card at once, the selection as the term, its whole sentences as the passage ---


def test_one_selected_word_makes_its_card_from_the_sentence_around_it(client):
    state = card_from(client, "skew", before="The median resists them. Outliers can ", after=" the mean considerably. More text.")
    assert state["result"] == "added" and len(state["paragraphs"]) == 1
    card = state["cards"][0]
    assert (card["front"], card["back"]) == ("skew", SENTENCE)
    assert [piece["text"] for p in state["paragraphs"] for s in p for piece in s["pieces"] if piece.get("picked")] == ["skew"]


def test_a_few_words_make_their_card_with_their_sentence(client):
    state = card_from(client, "can skew the", before="Outliers ", after=" mean considerably.")
    assert state["count"] == 1 and (state["cards"][0]["front"], state["cards"][0]["back"]) == ("can skew the", SENTENCE)
    assert state["cards"][0]["can_suggest"]   # three words: the panel offers Suggest meaning


def test_a_long_selection_offers_no_meaning(client):
    state = card_from(client, "founder is a variable that influences both the treatment and the outcome. Another",
                      before="Read this. A con", after=" sentence. Last one.")
    assert not state["cards"][0]["can_suggest"]   # its passage is the definition


def test_a_selection_across_two_sentences_is_the_term_and_both_whole_sentences_the_passage(client):
    state = card_from(client, "founder is a variable that influences both the treatment and the outcome. Another",
                      before="Read this. A con", after=" sentence. Last one.")
    card = state["cards"][0]
    assert card["front"] == "confounder is a variable that influences both the treatment and the outcome. Another"   # whole words
    assert card["back"] == DEFINITION + " Another sentence."
    assert card["can_cloze"]   # the term is in the passage


def test_a_whole_sentence_selected_is_its_own_term(client):
    state = card_from(client, SENTENCE)
    assert (state["cards"][0]["front"], state["cards"][0]["back"]) == ("Outliers can skew the mean considerably", SENTENCE)


def test_a_word_already_in_the_memory_is_offered_as_before(tmp_path):
    from sentmine.history import Entry
    memory = CardMemory(tmp_path / "cards.db")
    memory.add([Entry("word", "skew", "skew", SENTENCE, "skew", "2026-11-01")])
    client = create_app(Session(memory)).test_client()
    state = card_from(client, "skew", before="Outliers can ", after=" the mean.")
    assert state["result"] == "earlier" and state["count"] == 0 and "2026-11-01" in state["message"]


def test_clip_cards_can_be_edited_downloaded_and_deleted_under_clip(client):
    state = click(client, clip(client, SENTENCE), "skew")
    card_id = state["cards"][0]["id"]
    assert client.put(f"/clip/api/cards/{card_id}", json={"front": "f", "back": "b"}).status_code == 200
    assert client.get("/clip/api/deck?name=web").status_code == 200
    assert client.delete(f"/clip/api/cards/{card_id}").get_json()["count"] == 0


def test_a_clip_can_be_removed_and_cards_stay_marked_where_they_were(client):
    clip(client, "Causal inference")
    state = click(client, clip(client, SENTENCE), "skew")
    state = click(client, state, "mean")
    state = client.delete("/clip/api/clips/0").get_json()
    assert len(state["paragraphs"]) == 1 and state["count"] == 2
    picked = [piece["text"] for p in state["paragraphs"] for s in p for piece in s["pieces"] if piece.get("picked")]
    assert picked == ["skew", "mean"]   # still marked in the clip that moved up
    state = click(client, state, "skew")   # and a second click still removes its card
    assert state["count"] == 1


def test_removing_the_clip_a_card_came_from_keeps_the_card(client):
    click(client, clip(client, SENTENCE), "skew")
    state = client.delete("/clip/api/clips/0").get_json()
    assert state["paragraphs"] == [] and state["count"] == 1
    assert client.delete("/clip/api/clips/5").status_code == 400


def test_the_clip_page_holds_the_clips(client):
    clip(client, SENTENCE)
    page = client.get("/clip")
    assert page.status_code == 200 and b"Outliers" in page.data


@pytest.mark.parametrize("text", ["   ", ""])
def test_a_clip_without_text_is_refused(text):
    with pytest.raises(Problem):
        Session().add(text)
    with pytest.raises(Problem):
        Session().add_clip(text)

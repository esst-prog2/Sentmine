"""reading-place: the state names the text read, so the page can keep the reader's place in it."""

from sentmine.app import create_app


def text_id(client, text):
    return client.post("/api/text", json={"text": text}).get_json()["text_id"]


def test_no_text_has_no_id():
    assert create_app().test_client().get("/api/state").get_json()["text_id"] == ""


def test_the_same_words_give_the_same_id_and_other_words_another():
    client = create_app().test_client()
    first = text_id(client, "Outliers can skew it.")
    assert first and text_id(client, "Outliers   can\nskew it.") == first  # the same words after tidying
    assert text_id(client, "Another text.") != first


def test_every_answer_names_the_text():
    client = create_app().test_client()
    first = text_id(client, "Outliers can skew it.")
    assert client.post("/api/word", json={"sentence": 0, "word": 2}).get_json()["text_id"] == first

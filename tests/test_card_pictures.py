"""card-pictures: a part of a PDF page (a formula or a graph) on the back of a card, in the deck and in Anki."""

import io
import json
import struct
import zipfile

import pytest
from apkg_helper import read_notes
from pdf_helper import make_pdf
from reading_helper import place_of, post_clip
from test_send_to_anki import FakeAnki

from sentmine.anki import send_notes
from sentmine.app import create_app
from sentmine.deck import Note, write_notes
from sentmine.pages import PART_SCALE, locate, part
from sentmine.reading import Problem, Session

TEXT = [["Outliers can skew the mean considerably.", "The median resists outliers."]]
PNG = b"\x89PNG\r\n\x1a\n" + b"a picture"


def png_size(data: bytes) -> tuple[int, int]:
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


@pytest.fixture
def pages():
    data = make_pdf(TEXT)
    session = Session()
    session.load(" ".join(TEXT[0]))
    return locate(data, session.sentences)


# --- the part of the page ------------------------------------------------------------------


def test_a_box_of_the_page_is_drawn_sharp(pages):
    width_points, height_points = pages.sizes[0]
    png = part(pages, 0, (0.1, 0.1, 0.5, 0.2))
    width, height = png_size(png)
    assert abs(width - 0.5 * width_points * PART_SCALE) <= 2
    assert abs(height - 0.2 * height_points * PART_SCALE) <= 2


@pytest.mark.parametrize("number, box, message", [
    (0, (0.1, 0.1, 0.001, 0.2), "larger box"),
    (0, (0.8, 0.1, 0.5, 0.2), "inside one page"),
    (5, (0.1, 0.1, 0.5, 0.2), "not in the PDF"),
])
def test_a_box_that_is_too_small_or_outside_is_refused(pages, number, box, message):
    with pytest.raises(ValueError, match=message):
        part(pages, number, box)


# --- the card --------------------------------------------------------------------------------


def word_card(session: Session):
    session.load("Outliers can skew the mean considerably.")
    sentence, word = place_of(session.layout(), "skew")
    session.pick_word(sentence, word)
    return session.cards[0]


def test_a_picture_goes_under_the_answer_and_is_named_by_its_content():
    session = Session()
    card = word_card(session)
    session.add_picture(card.id, PNG)
    session.add_picture(card.id, PNG)   # the same picture again is stored once
    note = card.note
    assert len(card.pictures) == 1
    name = card.pictures[0][0]
    assert name.startswith("sentmine-") and name.endswith(".png")
    assert note.fields[1] == "Outliers can <b>skew</b> the mean considerably." + f'<div><img src="{name}"></div>'
    assert note.media == ((name, PNG),)


def test_a_cloze_card_keeps_the_picture_in_its_passage():
    session = Session()
    session.load("A confounder is a variable that influences both the treatment and the outcome.")
    session.add_definition("confounder", "A confounder is a variable that influences both the treatment and the outcome.")
    card = session.cards[0]
    session.set_cloze(card.id, True)
    session.add_picture(card.id, PNG)
    note = card.note
    assert note.cloze and "{{c1::confounder}}" in note.fields[0]
    assert note.fields[0].endswith(f'<div><img src="{card.pictures[0][0]}"></div>') and note.fields[1] == ""


def test_the_back_is_a_small_document_of_text_and_pictures():
    session = Session()
    card = word_card(session)
    session.add_picture(card.id, PNG)
    name = card.pictures[0][0]
    assert card.back == f"Outliers can skew the mean considerably.\n[[picture:{name}]]"   # a new picture goes at the end
    # the reader moves it between two lines of text
    session.edit(card.id, card.front, f"skew\n[[picture:{name}]]\nto distort")
    assert card.note.fields[1] == f'<b>skew</b><div><img src="{name}"></div>to distort'
    # a picture's place that is not this card's own is dropped; text that looks like markup stays text
    session.edit(card.id, card.front, f"skew <b>\n[[picture:sentmine-{'0' * 16}.png]]\n[[picture:{name}]]")
    assert card.note.fields[1] == f'<b>skew</b> &lt;b&gt;<div><img src="{name}"></div>'
    # taking the picture out of the text removes it from the card
    session.edit(card.id, card.front, "skew")
    assert card.pictures == [] and card.note.fields[1] == "<b>skew</b>" and card.note.media == ()


def test_a_suggested_meaning_keeps_the_pictures_on_the_back():
    session = Session()
    card = word_card(session)
    session.add_picture(card.id, PNG)
    name = card.pictures[0][0]
    session.suggest(card.id, lambda word, sentence: "to distort")
    assert card.back == f"Outliers can skew the mean considerably.\n[[picture:{name}]]\n\nto distort"


def test_a_picture_moved_to_the_front_stays_on_the_card_and_the_meaning_is_asked_without_it():
    session = Session()
    card = word_card(session)
    sentence = card.back
    session.add_picture(card.id, PNG)
    name = card.pictures[0][0]
    session.edit(card.id, f"skew\n[[picture:{name}]]", sentence)
    assert card.front == f"skew\n[[picture:{name}]]" and len(card.pictures) == 1
    assert f'<img src="{name}">' in card.front_html and "<b>skew</b>" in card.back_html
    asked = []
    session.suggest(card.id, lambda word, sentence: asked.append(sentence) or "to distort")
    assert asked == [sentence] and card.back == sentence + "\n\nto distort"


def test_a_cloze_card_hides_the_term_and_shows_the_front_pictures_after_the_answer():
    session = Session()
    passage = "A confounder is a variable that influences both the treatment and the outcome."
    session.load(passage)
    session.add_definition("confounder", passage)
    card = session.cards[0]
    session.add_picture(card.id, PNG)
    name = card.pictures[0][0]
    session.edit(card.id, f"confounder\n[[picture:{name}]]", passage)
    session.set_cloze(card.id, True)
    first, extra = card.note.fields
    assert "{{c1::confounder}}" in first and "[[picture" not in first and f'<img src="{name}">' in extra
    assert card.note.media == ((name, PNG),)


def test_the_memory_keeps_the_text_and_says_where_a_picture_was(tmp_path):
    from sentmine.memory import CardMemory
    session = Session(CardMemory(tmp_path / "cards.db"))
    card = word_card(session)
    session.add_picture(card.id, PNG)
    session.export(tmp_path / "d.apkg")
    assert session.memory.find("word", "skew").back == "Outliers can skew the mean considerably.\n[picture]"


def test_the_memory_says_where_a_picture_was_on_the_front(tmp_path):
    from sentmine.memory import CardMemory
    session = Session(CardMemory(tmp_path / "cards.db"))
    card = word_card(session)
    sentence = card.front
    session.add_picture(card.id, PNG)
    name = card.pictures[0][0]
    session.edit(card.id, f"[[picture:{name}]]\n{sentence}", "skew")
    session.export(tmp_path / "d.apkg")
    assert session.memory.find("word", "skew").front == f"[picture]\n{sentence}"


# --- to Anki ---------------------------------------------------------------------------------


def test_the_deck_file_contains_the_picture(tmp_path):
    note = Note(("front", 'back<div><img src="sentmine-ab.png"></div>'), media=(("sentmine-ab.png", PNG),))
    write_notes([note], tmp_path / "deck.apkg")
    with zipfile.ZipFile(tmp_path / "deck.apkg") as z:
        media = json.loads(z.read("media"))
        assert list(media.values()) == ["sentmine-ab.png"]
        assert z.read(next(iter(media))) == PNG
    (_, front, back), = read_notes(tmp_path / "deck.apkg", tmp_path)[0]
    assert 'src="sentmine-ab.png"' in back


class AnkiWithMedia(FakeAnki):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stored = {}

    def __call__(self, body):
        if body["action"] == "storeMediaFile":
            self.actions.append("storeMediaFile")
            self.stored[body["params"]["filename"]] = body["params"]["data"]
            return {"result": body["params"]["filename"], "error": None}
        return super().__call__(body)


def test_send_to_anki_stores_the_picture_before_adding_the_note():
    fake = AnkiWithMedia()
    note = Note(("front", 'back<div><img src="sentmine-ab.png"></div>'), media=(("sentmine-ab.png", PNG),))
    assert send_notes([note], "deck", post=fake) == (1, 0)
    assert list(fake.stored) == ["sentmine-ab.png"]
    assert fake.actions.index("storeMediaFile") < fake.actions.index("addNotes")


def test_a_note_already_in_anki_sends_no_picture():
    fake = AnkiWithMedia(notes=[("deck", "front")])
    note = Note(("front", "back"), media=(("sentmine-ab.png", PNG),))
    assert send_notes([note], "deck", post=fake) == (0, 1)
    assert fake.stored == {}


# --- the app ---------------------------------------------------------------------------------


@pytest.fixture
def client():
    return create_app().test_client()


def upload(client):
    data = make_pdf(TEXT)
    return client.post("/api/file", data={"file": (io.BytesIO(data), "book.pdf")}, content_type="multipart/form-data").get_json()


def test_a_box_on_the_page_puts_a_picture_on_the_card(client):
    state = upload(client)
    sentence, word = place_of(state["paragraphs"], "skew")
    card = client.post("/api/word", json={"sentence": sentence, "word": word}).get_json()["cards"][0]
    state = client.post(f"/api/cards/{card['id']}/pictures", json={"page": 0, "box": [0.1, 0.1, 0.5, 0.2]}).get_json()
    (name, address), = state["cards"][0]["pictures"].items()
    picture = client.get(address)
    assert picture.status_code == 200 and picture.mimetype == "image/png"
    assert png_size(picture.data)[0] > 100
    assert f'<img src="{address}">' in state["cards"][0]["back_html"]   # shown where it is in the text
    assert state["cards"][0]["back"].endswith(f"[[picture:{name}]]")
    assert "Picture added to the card for 'skew'" in state["message"]
    state = client.put(f"/api/cards/{card['id']}", json={"front": card["front"], "back": "skew"}).get_json()
    assert state["cards"][0]["pictures"] == {}
    assert client.get(address).status_code == 400


@pytest.mark.parametrize("body", [{"page": 0, "box": [0.1, 0.1]}, {"page": 0, "box": "all"}, {"page": 0, "box": [0.1, 0.1, 0.001, 0.2]}, {"page": 9, "box": [0.1, 0.1, 0.5, 0.2]}])
def test_a_bad_box_is_refused_with_a_message(client, body):
    state = upload(client)
    sentence, word = place_of(state["paragraphs"], "skew")
    card = client.post("/api/word", json={"sentence": sentence, "word": word}).get_json()["cards"][0]
    response = client.post(f"/api/cards/{card['id']}/pictures", json=body)
    assert response.status_code == 400 and response.get_json()["error"]


# --- pictures from web pages, and picture only ----------------------------------------------

import base64


def clip_card(client):
    state = post_clip(client, {"text": "Salami is a cured sausage.", "kind": "word"}).get_json()
    sentence, word = place_of(state["paragraphs"], "cured")
    return client.post("/clip/api/word", json={"sentence": sentence, "word": word}).get_json()["cards"][-1]


def test_a_png_from_a_web_page_goes_on_a_clip_card(client):
    card = clip_card(client)
    real = part(locate(make_pdf(TEXT), [" ".join(TEXT[0])]), 0, (0.1, 0.1, 0.3, 0.1))
    state = client.post(f"/clip/api/cards/{card['id']}/pictures", json={"png": base64.b64encode(real).decode()}).get_json()
    (address,) = state["cards"][-1]["pictures"].values()
    assert address.startswith("/clip/api/cards/")
    assert client.get(address).data == real
    assert client.get("/api/state").get_json()["paragraphs"] == []   # the text in Read is untouched


@pytest.mark.parametrize("png, message", [
    (base64.b64encode(b"GIF89a not a png").decode(), "Only PNG"),
    ("not base64 !!", "could not be read"),
    ("huge", "too large"),
])
def test_a_picture_that_is_not_a_small_png_is_refused(client, png, message):
    if png == "huge":
        png = "A" * (8 * 1024 * 1024)   # built here: as a parameter it would become the test's (too long) name
    card = clip_card(client)
    response = client.post(f"/clip/api/cards/{card['id']}/pictures", json={"png": png})
    assert response.status_code == 400 and message in response.get_json()["error"]


def test_a_clip_has_no_pdf_to_draw_a_box_on(client):
    card = clip_card(client)
    response = client.post(f"/clip/api/cards/{card['id']}/pictures", json={"page": 0, "box": [0.1, 0.1, 0.5, 0.2]})
    assert response.status_code == 400 and "right-click" in response.get_json()["error"]


def test_pictures_go_to_the_chosen_card_and_a_new_card_is_chosen_by_itself(client):
    first = clip_card(client)
    state = post_clip(client, {"text": "Pork is the meat of pigs.", "kind": "word"}).get_json()
    sentence, word = place_of(state["paragraphs"], "meat")
    second = client.post("/clip/api/word", json={"sentence": sentence, "word": word}).get_json()["cards"][-1]
    assert client.get("/clip/api/state").get_json()["chosen_card"] == second["id"]
    state = client.put(f"/clip/api/cards/{first['id']}/chosen").get_json()
    assert state["chosen_card"] == first["id"]
    client.delete(f"/clip/api/cards/{first['id']}")
    assert client.get("/clip/api/state").get_json()["chosen_card"] == second["id"]   # gone: the newest again
    assert client.put("/clip/api/cards/99/chosen").status_code == 400

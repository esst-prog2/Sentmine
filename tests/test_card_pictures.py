"""card-pictures: a part of a PDF page (a formula or a graph) on the back of a card, in the deck and in Anki."""

import io
import json
import struct
import zipfile

import pytest
from apkg_helper import read_notes
from pdf_helper import make_pdf
from reading_helper import place_of
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
    assert note.fields[1] == "skew" + f'<div><img src="{name}"></div>'
    assert note.media == ((name, PNG),)


def test_a_cloze_card_shows_the_picture_after_the_answer():
    session = Session()
    session.load("A confounder is a variable that influences both the treatment and the outcome.")
    session.add_definition("confounder", "A confounder is a variable that influences both the treatment and the outcome.")
    card = session.cards[0]
    session.set_cloze(card.id, True)
    session.add_picture(card.id, PNG)
    note = card.note
    assert note.cloze and "{{c1::confounder}}" in note.fields[0]
    assert note.fields[1] == f'<div><img src="{card.pictures[0][0]}"></div>'


def test_a_picture_can_be_removed():
    session = Session()
    card = word_card(session)
    session.add_picture(card.id, PNG)
    session.remove_picture(card.id, 0)
    assert card.pictures == [] and card.note.fields[1] == "skew"
    with pytest.raises(Problem):
        session.remove_picture(card.id, 0)


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
    address = state["cards"][0]["pictures"][0]
    picture = client.get(address)
    assert picture.status_code == 200 and picture.mimetype == "image/png"
    assert png_size(picture.data)[0] > 100
    state = client.delete(f"/api/cards/{card['id']}/pictures/0").get_json()
    assert state["cards"][0]["pictures"] == []


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
    state = client.post("/clip/api/text", json={"text": "Salami is a cured sausage.", "kind": "word"}).get_json()
    sentence, word = place_of(state["paragraphs"], "cured")
    return client.post("/clip/api/word", json={"sentence": sentence, "word": word}).get_json()["cards"][-1]


def test_a_png_from_a_web_page_goes_on_a_clip_card(client):
    card = clip_card(client)
    real = part(locate(make_pdf(TEXT), [" ".join(TEXT[0])]), 0, (0.1, 0.1, 0.3, 0.1))
    state = client.post(f"/clip/api/cards/{card['id']}/pictures", json={"png": base64.b64encode(real).decode()}).get_json()
    address = state["cards"][-1]["pictures"][0]
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
    state = client.post("/clip/api/text", json={"text": "Pork is the meat of pigs.", "kind": "word"}).get_json()
    sentence, word = place_of(state["paragraphs"], "meat")
    second = client.post("/clip/api/word", json={"sentence": sentence, "word": word}).get_json()["cards"][-1]
    assert client.get("/clip/api/state").get_json()["chosen_card"] == second["id"]
    state = client.put(f"/clip/api/cards/{first['id']}/chosen").get_json()
    assert state["chosen_card"] == first["id"]
    client.delete(f"/clip/api/cards/{first['id']}")
    assert client.get("/clip/api/state").get_json()["chosen_card"] == second["id"]   # gone: the newest again
    assert client.put("/clip/api/cards/99/chosen").status_code == 400

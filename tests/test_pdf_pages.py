"""pdf-pages: a PDF shown as its own pages. PDFs are built by hand with pdf_helper."""

import io
import struct
from concurrent.futures import ThreadPoolExecutor

import pytest
from pdf_helper import make_pdf

from sentmine.app import create_app
from sentmine.document import read_pdf
from sentmine.pages import PICTURE_WIDTH, locate, picture
from sentmine.reading import Session, clickable_words

TWO_PAGES = [
    ["The standard deviation measures spread.", "Outliers can skew it consid-", "erably in small samples."],
    ["A second page with more words."],
]


def located(pages):
    data = make_pdf(pages)
    session = Session()
    session.load(read_pdf(data)[0])
    return session, locate(data, session.sentences)


def boxes_of(found, text):
    """The boxes of every word written `text`, ignoring case, as (page, box)."""
    return [(number, box) for number, page in enumerate(found.boxes) for box in page if _word(found, box).lower() == text.lower()]


def _word(found, box):
    return found.words[(box[0], box[1])]


@pytest.fixture
def two_pages():
    session, found = located(TWO_PAGES)
    found.words = {(s, i): w.text for s, sentence in enumerate(session.sentences) for i, w in enumerate(clickable_words(sentence))}
    return session, found


# --- finding the words on the pages ---------------------------------------------------------------


def test_every_word_is_found(two_pages):
    session, found = two_pages
    placed = {(box[0], box[1]) for page in found.boxes for box in page}
    assert placed == set(found.words)


def test_each_word_is_on_its_page(two_pages):
    _, found = two_pages
    assert [page for page, _ in boxes_of(found, "spread")] == [0]
    assert [page for page, _ in boxes_of(found, "second")] == [1]


def test_boxes_are_parts_of_the_page_in_reading_order(two_pages):
    _, found = two_pages
    for page in found.boxes:
        for _, _, left, top, width, height in page:
            assert 0 <= left < 1 and 0 <= top < 1 and 0 < width < 1 and 0 < height < 0.1
    line = [box for _, box in boxes_of(found, "The") + boxes_of(found, "standard") + boxes_of(found, "deviation")]
    assert line[0][2] < line[1][2] < line[2][2]  # left to right
    assert line[0][3] == pytest.approx(line[2][3], abs=0.002)  # on one line
    assert found.boxes[0] == sorted(found.boxes[0], key=lambda box: (box[0], box[1]))


def test_a_word_broken_at_a_line_end_has_a_box_on_each_line(two_pages):
    _, found = two_pages
    halves = boxes_of(found, "considerably")
    assert len(halves) == 2
    (_, first), (_, second) = halves
    assert second[3] > first[3] and second[2] < first[2]  # the second half starts the next line


def test_a_running_head_has_no_box():
    pages = [["Chapter One", f"Sentence number {word} ends here."] for word in ["one", "two", "three"]]
    session, found = located(pages)
    assert "Chapter" not in " ".join(session.sentences)
    assert sum(len(page) for page in found.boxes) == sum(len(clickable_words(s)) for s in session.sentences)


def test_numbers_between_words_do_not_lose_the_place():
    session, found = located([["Male 112 High school 231 College 595.", "The table ends here."]])
    placed = {(box[0], box[1]) for page in found.boxes for box in page}
    words = {(s, i) for s, sentence in enumerate(session.sentences) for i, _ in enumerate(clickable_words(sentence))}
    assert placed == words


def test_the_same_words_twice_are_each_found_where_they_are():
    session, found = located([["Assuming that there are twice as many tables."], ["Assuming that there are twice as many tables."]])
    pages_of_first = {page for page, page_boxes in enumerate(found.boxes) for box in page_boxes if box[0] == 0}
    pages_of_second = {page for page, page_boxes in enumerate(found.boxes) for box in page_boxes if box[0] == 1}
    assert (pages_of_first, pages_of_second) == ({0}, {1})


# --- pictures -------------------------------------------------------------------------------------


def png_size(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


def test_a_page_as_a_picture():
    _, found = located(TWO_PAGES)
    width, height = png_size(picture(found, 1))
    assert width == PICTURE_WIDTH and height == pytest.approx(PICTURE_WIDTH * 792 / 612, abs=2)


def test_pages_can_be_drawn_and_read_at_the_same_time():
    """The browser asks for several pages at once; without one lock around pdfium this crashed."""
    data = make_pdf([[f"Page {n} words."] for n in range(8)])
    _, found = located([[f"Page {n} words."] for n in range(8)])
    with ThreadPoolExecutor(max_workers=8) as pool:
        pictures = list(pool.map(lambda number: picture(found, number, 200), range(8)))
        read = list(pool.map(lambda _: read_pdf(data)[1], range(8)))
    assert all(png_size(one)[0] == 200 for one in pictures) and read == [8] * 8


# --- the app --------------------------------------------------------------------------------------


def upload(client, name="book.pdf", data=None):
    data = make_pdf(TWO_PAGES) if data is None else data
    return client.post("/api/file", data={"file": (io.BytesIO(data), name)}, content_type="multipart/form-data")


def test_a_pdf_is_shown_as_pages():
    client = create_app().test_client()
    state = upload(client).get_json()
    assert state["pdf"]["sizes"] == [[612, 792], [612, 792]]
    boxes = client.get("/api/pages/0/words").get_json()["boxes"]
    assert len(boxes) == 14 and all(len(box) == 6 for box in boxes)  # 13 words; "consid-erably" has a box on each line
    picture_response = client.get(f"/api/pages/1.png?v={state['pdf']['version']}")
    assert picture_response.mimetype == "image/png" and png_size(picture_response.data)[0] == PICTURE_WIDTH


def test_a_word_picked_on_a_page_makes_its_card():
    client = create_app().test_client()
    upload(client)
    sentence, word = client.get("/api/pages/0/words").get_json()["boxes"][7][:2]  # "skew"
    made = client.post("/api/word", json={"sentence": sentence, "word": word}).get_json()
    assert made["cards"][0]["front"] == "Outliers can skew it considerably in small samples."


def test_each_pdf_read_has_a_new_version():
    client = create_app().test_client()
    first = upload(client).get_json()["pdf"]["version"]
    assert upload(client).get_json()["pdf"]["version"] != first


@pytest.mark.parametrize("load", [
    lambda client: client.post("/api/text", json={"text": "A pasted text."}),
    lambda client: upload(client, "notes.txt", b"A text file."),
])
def test_a_text_that_is_not_a_pdf_has_no_pages(load):
    client = create_app().test_client()
    upload(client)
    assert load(client).get_json()["pdf"] is None
    assert client.get("/api/pages/0/words").status_code == 400


@pytest.mark.parametrize("path", ["/api/pages/2/words", "/api/pages/2.png"])
def test_a_page_that_is_not_there(path):
    client = create_app().test_client()
    upload(client)
    response = client.get(path)
    assert response.status_code == 400 and "not in the PDF" in response.get_json()["error"]

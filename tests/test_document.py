"""document-reader. Pages are invented by hand; PDFs are built by pdf_helper, never real books."""

import io

import pytest
from pdf_helper import make_pdf
from pypdf import PdfWriter
from reading_helper import place_of

from sentmine.app import create_app
from sentmine.document import DocumentProblem, clean_pages, read_file, read_pdf
from sentmine.reading import Session

LONG = "This is an ordinary line of text that fills the whole width of a page"


def with_head(number, *lines):
    return "\n".join((f"Preliminaries: Statistical and Causal Models {number}", *lines))


# --- cleaning ------------------------------------------------------------------------------


def test_a_running_head_with_its_page_number_is_removed():
    pages = [with_head(n, f"{LONG} number {word}.") for n, word in enumerate(("one", "two", "three", "four"))]
    assert "Preliminaries" not in clean_pages(pages)


def test_marks_at_the_top_of_every_page_are_removed():
    pages = [f"k\nk k\n{LONG} number {n}." for n in ("one", "two", "three", "four")]
    assert clean_pages(pages).count("k k") == 0
    assert clean_pages(pages).startswith(LONG)


def test_a_running_head_below_other_marks_is_removed_too():
    pages = [f"k\nk k\nk\nModels {n}\n{LONG} number {word}." for n, word in enumerate(("one", "two", "three", "four"))]
    text = clean_pages(pages)
    assert "Models" not in text and text.startswith(LONG)


def test_a_bare_page_number_is_removed():
    assert clean_pages([LONG + ".\n" + LONG + ".\n12"]).count("12") == 0


def test_a_line_on_two_pages_is_not_a_running_head():
    pages = ["Chapter one\n" + LONG + ".", "Chapter one\n" + LONG + "."]
    assert clean_pages(pages).count("Chapter one") == 2


def test_a_repeated_line_in_the_middle_of_a_page_stays():
    pages = ["\n".join([f"{word} {LONG}"] * 4 + ["The same sentence."] + [f"{LONG} {word}."] * 4) for word in ("a", "b", "c")]
    assert clean_pages(pages).count("The same sentence.") == 3


def test_identical_pages_keep_their_text():
    assert "Each page says this." in clean_pages(["Each page says this."] * 4)


def test_a_hyphenated_word_is_rejoined():
    assert "significantly more likely" in clean_pages(["women are signifi-\ncantly more likely to take it."])


def test_a_hyphen_before_a_capital_stays():
    assert "post-\nBrexit" in clean_pages(["the post-\nBrexit years are long."])


def test_a_short_line_that_ends_a_sentence_ends_a_paragraph():
    page = "\n".join([LONG, LONG, "It ended here.", LONG, LONG + "."])
    first, second = clean_pages([page]).split("\n\n")
    assert first.endswith("It ended here.") and second.startswith(LONG)


def test_a_full_line_that_ends_a_sentence_does_not_end_a_paragraph():
    assert "\n\n" not in clean_pages(["\n".join([LONG, LONG + ".", LONG, LONG + "."])])


def test_a_sentence_goes_on_across_a_page_break():
    text = clean_pages(["\n".join([LONG, "and it goes on past the end of"]), "the page without stopping here."])
    assert "\n\n" not in text and text.endswith("end of\nthe page without stopping here.")


def test_a_word_broken_across_a_page_break_is_rejoined():
    assert "significantly more" in clean_pages([LONG + "\nwomen are signifi-", "cantly more likely."])


def test_a_page_that_ends_a_sentence_ends_a_paragraph():
    assert clean_pages(["The first page ends.", "The second page starts."]).count("\n\n") == 1


def test_the_words_are_not_otherwise_changed():
    assert clean_pages(["E[X|Y = y] = 0.5y costs 3.5 units (see Eq. 1.20)."]) == "E[X|Y = y] = 0.5y costs 3.5 units (see Eq. 1.20)."


def test_empty_pages_are_skipped():
    assert clean_pages(["", "  \n ", "Some text."]) == "Some text."


def test_a_card_from_a_sentence_across_two_pages_shows_the_whole_sentence():
    reading = Session()
    reading.load(clean_pages(["\n".join([LONG + ".", LONG + ".", "Outliers can"]), "skew it considerably."]))
    _, card = reading.pick_word(*place_of(reading, "skew"))
    assert card.front == "Outliers can skew it considerably."


# --- reading files -----------------------------------------------------------------------------


def test_a_pdf_with_text():
    text, pages, empty = read_pdf(make_pdf([["The first page ends."], ["The second page ends."], ["The third."]]))
    assert (pages, empty) == (3, 0)
    assert "The second page ends." in text


def test_a_page_with_no_text_is_counted():
    _, message = read_file("notes.PDF", make_pdf([["Some text here."], [], ["More text here."]]))
    assert message == "Read 3 pages. 1 had no text."


def test_one_page_in_the_singular():
    assert read_file("a.pdf", make_pdf([["Some text here."]]))[1] == "Read 1 page."


def test_a_text_file():
    assert read_file("notes.txt", "﻿Plain text, café.".encode("utf-8")) == ("Plain text, café.", "Read the text file.")


@pytest.mark.parametrize(
    "name, data, words",
    [
        ("a.pdf", make_pdf([[], []]), "scanned"),
        ("a.pdf", b"this is not a pdf at all", "could not be read as a PDF"),
        ("a.pdf", b"", "empty"),
        ("a.docx", b"PK\x03\x04", "Only PDF and text"),
        ("a", b"data", "Only PDF and text"),
        ("a.txt", b"\xff\xfe\x00bad", "not in UTF-8"),
    ],
)
def test_files_that_cannot_be_read(name, data, words):
    with pytest.raises(DocumentProblem, match=words):
        read_file(name, data)


def test_a_pdf_locked_with_a_password():
    writer = PdfWriter(clone_from=io.BytesIO(make_pdf([["Secret text."]])))
    writer.encrypt("a-password")
    locked = io.BytesIO()
    writer.write(locked)
    with pytest.raises(DocumentProblem, match="password"):
        read_pdf(locked.getvalue())


# --- the app ---------------------------------------------------------------------------------


def upload(client, name, data):
    return client.post("/api/file", data={"file": (io.BytesIO(data), name)}, content_type="multipart/form-data")


def test_uploading_a_pdf_puts_its_text_on_the_page():
    client = create_app().test_client()
    state = upload(client, "notes.pdf", make_pdf([["Outliers can skew it considerably."]])).get_json()
    assert state["message"] == "Read 1 page."
    sentence, word = place_of(state["paragraphs"], "skew")
    made = client.post("/api/word", json={"sentence": sentence, "word": word}).get_json()
    assert made["cards"][0]["front"] == "Outliers can skew it considerably."


def test_a_refused_file_leaves_the_text_and_cards():
    client = create_app().test_client()
    client.post("/api/text", json={"text": "Polls skew young."})
    sentence, word = place_of(client.get("/api/state").get_json()["paragraphs"], "skew")
    client.post("/api/word", json={"sentence": sentence, "word": word})
    response = upload(client, "scan.pdf", make_pdf([[]]))
    assert response.status_code == 400 and "scanned" in response.get_json()["error"]
    state = client.get("/api/state").get_json()
    assert state["count"] == 1 and state["paragraphs"]


def test_a_request_with_no_file_is_refused():
    assert create_app().test_client().post("/api/file").status_code == 400


def test_a_file_over_the_limit_is_refused_with_a_message(monkeypatch):
    app = create_app()
    app.config["MAX_CONTENT_LENGTH"] = 10
    response = upload(app.test_client(), "big.txt", b"x" * 100)
    assert response.status_code == 413 and "50 MB" in response.get_json()["error"]

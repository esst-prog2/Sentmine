"""pdf-links: the PDF's own links and bookmarks, read from it so the reader can follow them in sentmine."""

import io

import pytest
from pdf_helper import make_pdf
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link

from sentmine.app import create_app
from sentmine.pages import locate

PAGES = [["The first page points to the second."], ["Chapter two starts here."]]


def with_links(data: bytes) -> bytes:
    writer = PdfWriter()
    writer.append(PdfReader(io.BytesIO(data)))
    writer.add_annotation(page_number=0, annotation=Link(rect=(50, 700, 200, 720), target_page_index=1))
    writer.add_annotation(page_number=0, annotation=Link(rect=(50, 650, 200, 670), url="https://example.org/book"))
    writer.add_annotation(page_number=0, annotation=Link(rect=(50, 600, 200, 620), url="javascript:alert(1)"))
    writer.add_outline_item("Chapter two", 1)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


@pytest.fixture
def pdf():
    return with_links(make_pdf(PAGES))


def test_the_links_and_bookmarks_of_a_pdf_are_read(pdf):
    pages = locate(pdf, ["The first page points to the second.", "Chapter two starts here."])
    first = pages.links[0]
    assert {"page": 1} == {k: v for k, v in first[0].items() if k == "page"}
    assert [link.get("url") for link in first if "url" in link] == ["https://example.org/book"]   # javascript: is left out
    left, top, width, height = first[0]["box"]
    assert 0 <= left < 1 and 0 <= top < 1 and width > 0 and height > 0
    assert pages.links[1] == []
    assert pages.outline == [(0, "Chapter two", 1)]


def test_the_app_sends_links_with_the_words_and_the_outline_with_the_pdf(pdf):
    client = create_app().test_client()
    state = client.post("/api/file", data={"file": (io.BytesIO(pdf), "notes.pdf")}, content_type="multipart/form-data").get_json()
    assert state["pdf"]["outline"] == [{"level": 0, "title": "Chapter two", "page": 1}]
    links = client.get("/api/pages/0/words").get_json()["links"]
    assert sorted(("page" in link, "url" in link) for link in links) == [(False, True), (True, False)]

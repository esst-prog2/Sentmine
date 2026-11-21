"""smooth-switch: the pages come with their first data inside, and page words are cached by version."""

import json
import re

import pytest
from test_pdf_pages import upload

from sentmine.app import create_app
from sentmine.history import Entry
from sentmine.memory import CardMemory
from sentmine.reading import Session

SKEW = Entry("word", "skew", "Outliers can skew it considerably.", "skew", "skew", "2026-10-09")


@pytest.fixture
def client(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    memory.add([SKEW])
    return create_app(Session(memory)).test_client()


def first_data(page: bytes) -> dict:
    found = re.findall(rb'<script type="application/json" id="first-data">(.*?)</script>', page, re.DOTALL)
    assert len(found) == 1
    return json.loads(found[0])


def test_the_read_page_holds_the_reading_state(client):
    client.post("/api/text", json={"text": "Outliers can skew it considerably."})
    assert first_data(client.get("/").data) == client.get("/api/state").get_json()


def test_the_cards_page_holds_the_first_list(client):
    assert first_data(client.get("/cards").data) == client.get("/api/memory").get_json()


def test_text_that_looks_like_markup_cannot_end_the_script(client):
    client.post("/api/text", json={"text": "The tag </script><b>bold</b> is text here."})
    page = client.get("/").data
    assert b"</script><b>" not in page and b"><b>" not in page
    assert first_data(page) == client.get("/api/state").get_json()   # read back whole, the same text


def test_page_words_are_cached_only_under_this_pdfs_version(client):
    version = upload(client).get_json()["pdf"]["version"]
    assert client.get(f"/api/pages/0/words?v={version}").headers["Cache-Control"] == "private, max-age=3600"
    assert client.get("/api/pages/0/words").headers["Cache-Control"] == "no-store"
    assert client.get("/api/pages/0/words?v=0000").headers["Cache-Control"] == "no-store"

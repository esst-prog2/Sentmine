"""card-source: each card remembers where it came from; My cards shows it and counts cards per source."""

import io
import sqlite3

import pytest
from apkg_helper import read_notes
from pdf_helper import make_pdf
from reading_helper import place_of, post_clip

from sentmine.app import create_app
from sentmine.history import Entry
from sentmine.memory import SCHEMA_VERSION, CardMemory
from sentmine.reading import Session

OLD_TABLE = """CREATE TABLE cards (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, key TEXT NOT NULL, front TEXT NOT NULL,
    back TEXT NOT NULL, word TEXT NOT NULL DEFAULT '', made_on TEXT NOT NULL, UNIQUE (kind, key, front, back))"""


@pytest.fixture
def client(tmp_path):
    return create_app(Session(CardMemory(tmp_path / "cards.db"))).test_client()


def click(client, prefix, word):
    state = client.get(prefix + "/api/state").get_json()
    sentence, number = place_of(state["paragraphs"], word)
    return client.post(prefix + "/api/word", json={"sentence": sentence, "word": number}).get_json()


def test_a_layout_3_memory_gets_the_source_columns_and_a_copy_is_kept(tmp_path):
    path = tmp_path / "cards.db"
    with sqlite3.connect(path) as db:   # a memory as layout 3 left it, with one card
        db.execute(OLD_TABLE)
        db.execute("CREATE INDEX cards_by_key ON cards (kind, key)")
        db.execute("CREATE TABLE meetings (kind TEXT NOT NULL, key TEXT NOT NULL, text_id TEXT NOT NULL, "
                   "made INTEGER NOT NULL DEFAULT 0, day TEXT NOT NULL, PRIMARY KEY (kind, key, text_id))")
        db.execute("INSERT INTO cards (kind, key, front, back, word, made_on) VALUES ('word', 'skew', 'f', 'skew', 'skew', '2026-10-09')")
        db.execute("PRAGMA user_version = 3")
    memory = CardMemory(path)
    assert memory.problem == "" and memory.count() == 1
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION == 4
    assert memory.find("word", "skew").source == ""
    copy = tmp_path / "cards.db.before-layout-4"
    with sqlite3.connect(copy) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 3
        assert db.execute("SELECT COUNT(*) FROM cards").fetchone()[0] == 1


def test_a_card_from_a_pdf_says_its_file_and_page(client, tmp_path):
    data = make_pdf([["The first page is short."], ["Outliers can skew the mean considerably."]])
    client.post("/api/file", data={"file": (io.BytesIO(data), "primer.pdf")}, content_type="multipart/form-data")
    card = click(client, "", "skew")["cards"][-1]
    assert card["origin"] == "primer.pdf, p. 2"
    deck = client.get("/api/deck?name=d")
    (tmp_path / "d.apkg").write_bytes(deck.data)
    (_, front, back), = read_notes(tmp_path / "d.apkg", tmp_path)[0]
    assert back.startswith("Outliers can <b>skew</b>") and "Source: primer.pdf, p. 2</div>" in back
    remembered = client.get("/api/memory").get_json()
    assert remembered["cards"][0]["source"] == "primer.pdf, p. 2"
    assert remembered["progress"]["sources"] == [{"source": "primer.pdf", "cards": 1}]


def test_a_card_from_a_web_page_says_its_title_and_links_its_address(client, tmp_path):
    source = {"title": "Salami - Wikipedia", "url": "https://en.wikipedia.org/wiki/Salami"}
    post_clip(client, {"text": "Salami is a cured sausage.", "kind": "word", "source": source})
    post_clip(client, {"text": "Pork is the meat of pigs.", "kind": "word",
                                        "source": {"title": "<b>Pork</b>", "url": "javascript:alert(1)"}})
    first = click(client, "/clip", "cured")["cards"][-1]
    second = click(client, "/clip", "meat")["cards"][-1]
    assert (first["origin"], first["origin_url"]) == ("Salami - Wikipedia", "https://en.wikipedia.org/wiki/Salami")
    assert (second["origin"], second["origin_url"]) == ("<b>Pork</b>", "")   # an unsafe address is dropped
    (tmp_path / "d.apkg").write_bytes(client.get("/clip/api/deck?name=d").data)
    backs = [note[2] for note in read_notes(tmp_path / "d.apkg", tmp_path)[0]]
    assert 'Source: <a href="https://en.wikipedia.org/wiki/Salami">Salami - Wikipedia</a>' in backs[0]
    assert "Source: &lt;b&gt;Pork&lt;/b&gt;</div>" in backs[1]   # the title is text, never markup


def test_a_pasted_text_has_no_source_line(client, tmp_path):
    client.post("/api/text", json={"text": "Outliers can skew the mean."})
    card = click(client, "", "skew")["cards"][-1]
    assert card["origin"] == ""
    (tmp_path / "d.apkg").write_bytes(client.get("/api/deck?name=d").data)
    (_, front, back), = read_notes(tmp_path / "d.apkg", tmp_path)[0]
    assert back == "Outliers can <b>skew</b> the mean."


def test_cards_per_source_counts_the_most_first(tmp_path):
    memory = CardMemory(tmp_path / "cards.db")
    memory.add([Entry("word", w, f"The {w}.", w, w, "2026-11-17", "primer.pdf", "", f"p. {n}") for n, w in enumerate(["a", "b", "c"])]
               + [Entry("word", "d", "The d.", "d", "d", "2026-11-17", "Salami - Wikipedia", "https://en.wikipedia.org/wiki/Salami")]
               + [Entry("word", "e", "The e.", "e", "e", "2026-11-17")])
    assert memory.progress()["sources"] == [{"source": "primer.pdf", "cards": 3}, {"source": "Salami - Wikipedia", "cards": 1}]

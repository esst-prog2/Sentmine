"""memory-database: the SQLite card memory, its schema versions, the move from the old file, and My cards queries."""

import json
import sqlite3
from datetime import date

import pytest

from sentmine.history import Entry
from sentmine.lemma import base_form
from sentmine.memory import SCHEMA_VERSION, CardMemory, MemoryProblem, default_memory_path

SIGHED = Entry("word", "sigh", "Its owner sighed.", "sighed (sigh)", "sighed", "2026-10-17")
SKEW = Entry("word", "skew", "Outliers can skew it considerably.", "skew", "skew", "2026-10-09")
SD = Entry("definition", "standard deviation", "standard deviation", "How spread out the values are.", "", "2026-10-22")


def old_line(entry):
    return json.dumps({name: getattr(entry, name) for name in entry.__dataclass_fields__}) + "\n"


@pytest.fixture
def memory(tmp_path):
    return CardMemory(tmp_path / "cards.db")


def layout_version(path):
    with sqlite3.connect(path) as db:
        return db.execute("PRAGMA user_version").fetchone()[0]


# --- where it is kept --------------------------------------------------------------


def test_the_environment_variable_names_the_database(monkeypatch, tmp_path):
    monkeypatch.setenv("SENTMINE_DATABASE", str(tmp_path / "mine.db"))
    assert default_memory_path() == tmp_path / "mine.db"


def test_on_windows_it_is_in_appdata(monkeypatch, tmp_path):
    monkeypatch.delenv("SENTMINE_DATABASE", raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert default_memory_path() == tmp_path / "sentmine" / "cards.db"


def test_elsewhere_it_is_in_the_home_folder(monkeypatch, tmp_path):
    monkeypatch.delenv("SENTMINE_DATABASE", raising=False)
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    assert default_memory_path() == tmp_path / ".local" / "share" / "sentmine" / "cards.db"


# --- first use, adding, finding ----------------------------------------------------------


def test_first_use_creates_the_database_and_its_folder(tmp_path):
    path = tmp_path / "sentmine" / "cards.db"
    memory = CardMemory(path)
    assert (memory.problem, memory.entries) == ("", [])
    assert memory.add([SIGHED, SD]) == 2
    assert layout_version(path) == SCHEMA_VERSION
    assert CardMemory(path).entries == [SIGHED, SD]  # still there after the app starts again


def test_a_card_holds_everything(memory):
    memory.add([SIGHED])
    with sqlite3.connect(memory.path) as db:
        row = db.execute("SELECT kind, key, front, back, word, made_on FROM cards").fetchone()
    assert row == ("word", "sigh", "Its owner sighed.", "sighed (sigh)", "sighed", "2026-10-17")


def test_the_same_card_is_stored_once(memory):
    memory.add([SKEW])
    later = Entry(SKEW.kind, SKEW.key, SKEW.front, SKEW.back, SKEW.word, "2026-11-01")
    assert memory.add([SKEW, later]) == 0
    assert memory.entries == [SKEW]


def test_an_edited_card_is_a_new_one(memory):
    memory.add([SKEW])
    assert memory.add([Entry("word", "skew", SKEW.front, "skew: to distort", "skew", "2026-10-17")]) == 1


def test_finding_by_kind_and_key(memory):
    memory.add([SKEW, SD])
    assert memory.find("word", "skew") == SKEW
    assert memory.find("definition", "standard deviation") == SD
    assert memory.find("definition", "skew") is None
    assert memory.find("word", "variance") is None


def test_a_different_form_of_an_earlier_word_is_found(memory):
    memory.add([Entry("word", base_form("run"), "They run.", "run", "run", "2026-10-09")])
    assert memory.find("word", base_form("ran")) is not None


def test_the_most_recent_card_is_found(memory):
    newer = Entry("word", "skew", "Polls skew young.", "skew", "skew", "2026-10-17")
    memory.add([newer, SKEW])  # added in the other order: the date decides
    assert memory.find("word", "skew") == newer


# --- moving the old history file in --------------------------------------------------------


def test_cards_from_the_old_file_are_moved_in_with_their_dates(tmp_path):
    old = tmp_path / "history.jsonl"
    content = old_line(SKEW) + old_line(SIGHED) + old_line(SD)
    old.write_text(content, encoding="utf-8")
    memory = CardMemory(tmp_path / "cards.db")
    assert memory.entries == [SKEW, SIGHED, SD]
    assert "moved 3 cards" in memory.notice
    assert old.read_text(encoding="utf-8") == content  # the old file is left as it was


def test_the_old_file_is_moved_only_once(tmp_path):
    (tmp_path / "history.jsonl").write_text(old_line(SKEW), encoding="utf-8")
    CardMemory(tmp_path / "cards.db").delete(1)  # the reader deletes the moved card
    again = CardMemory(tmp_path / "cards.db")
    assert (again.entries, again.notice) == ([], "")  # it does not come back at the next start


def test_a_damaged_old_file_moves_nothing_and_is_tried_again(tmp_path):
    old = tmp_path / "history.jsonl"
    old.write_text(old_line(SKEW) + "damaged\n", encoding="utf-8")
    memory = CardMemory(tmp_path / "cards.db")
    assert "history.jsonl" in memory.problem and "line 2" in memory.problem
    assert old.read_text(encoding="utf-8") == old_line(SKEW) + "damaged\n"
    assert layout_version(tmp_path / "cards.db") == 1  # not marked as moved
    old.write_text(old_line(SKEW), encoding="utf-8")  # the reader fixes the file
    fixed = CardMemory(tmp_path / "cards.db")
    assert (fixed.problem, fixed.entries) == ("", [SKEW])


def test_no_old_file_is_fine(memory):
    assert (memory.problem, memory.notice) == ("", "")


# --- a memory that cannot be read ------------------------------------------------------------


def test_a_damaged_database_is_reported_finds_nothing_and_is_left_alone(tmp_path):
    path = tmp_path / "cards.db"
    path.write_bytes(b"this is not a database at all, just text " * 20)
    before = path.read_bytes()
    memory = CardMemory(path)
    assert "could not be opened" in memory.problem
    assert memory.find("word", "skew") is None
    assert memory.search("") == ([], 0)
    with pytest.raises(MemoryProblem):
        memory.add([SKEW])
    with pytest.raises(MemoryProblem):
        memory.delete(1)
    assert path.read_bytes() == before


def test_a_database_from_a_newer_version_is_refused(tmp_path):
    path = tmp_path / "cards.db"
    CardMemory(path).add([SKEW])
    with sqlite3.connect(path) as db:
        db.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")
    memory = CardMemory(path)
    assert "newer version" in memory.problem
    assert memory.find("word", "skew") is None


# --- search, progress, delete ---------------------------------------------------------------


def test_search_matches_word_key_front_or_back_in_any_case(memory):
    memory.add([SKEW, SIGHED, SD])
    assert [card.entry for card in memory.search("dev")[0]] == [SD]
    assert [card.entry for card in memory.search("OWNER")[0]] == [SIGHED]
    assert [card.entry.key for card in memory.search("s")[0]] == ["standard deviation", "sigh", "skew"]


def test_an_empty_search_lists_everything_newest_first(memory):
    memory.add([SKEW, SD, SIGHED])
    cards, total = memory.search("")
    assert [card.entry.date for card in cards] == ["2026-10-22", "2026-10-17", "2026-10-09"]
    assert total == 3


def test_search_shows_at_most_the_limit_but_counts_all(memory):
    memory.add([Entry("word", f"w{n}", f"Front {n}.", f"w{n}", f"w{n}", "2026-10-01") for n in range(5)])
    cards, total = memory.search("", limit=2)
    assert (len(cards), total) == (2, 5)


def test_search_treats_percent_and_underscore_as_plain_characters(memory):
    memory.add([SKEW, Entry("definition", "50% rule", "50% rule", "Half.", "", "2026-10-01")])
    assert [card.entry.key for card in memory.search("%")[0]] == ["50% rule"]
    assert memory.search("_")[1] == 0


def test_progress_this_week_and_by_month(memory):
    memory.add([SKEW, Entry("word", "a", "A.", "a", "a", "2026-10-19"), SD,
                Entry("word", "b", "B.", "b", "b", "2026-09-30"), Entry("word", "c", "C.", "c", "c", "2026-03-01")])
    progress = memory.progress(date(2026, 10, 22))  # a Thursday; the week began on Monday 19 October
    assert (progress["total"], progress["words"], progress["definitions"], progress["this_week"]) == (5, 4, 1, 2)
    assert progress["months"] == [
        {"month": "2026-05", "cards": 0}, {"month": "2026-06", "cards": 0}, {"month": "2026-07", "cards": 0},
        {"month": "2026-08", "cards": 0}, {"month": "2026-09", "cards": 1}, {"month": "2026-10", "cards": 3},
    ]


def test_progress_across_a_new_year(memory):
    months = memory.progress(date(2027, 2, 3))["months"]
    assert [m["month"] for m in months] == ["2026-09", "2026-10", "2026-11", "2026-12", "2027-01", "2027-02"]


def test_deleting_forgets_the_card(memory):
    memory.add([SKEW, SD])
    skew_id = next(card.id for card in memory.search("skew")[0])
    memory.delete(skew_id)
    assert memory.find("word", "skew") is None
    assert memory.entries == [SD]
    with pytest.raises(MemoryProblem, match="not in the memory"):
        memory.delete(skew_id)

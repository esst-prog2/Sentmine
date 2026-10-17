import json

import pytest

from sentmine.history import Entry, History, HistoryProblem, default_history_path
from sentmine.lemma import base_form

SIGHED = Entry("word", "sigh", "Its owner sighed.", "sighed (sigh)", "sighed", "2026-10-17")
SKEW = Entry("word", "skew", "Outliers can skew it considerably.", "skew", "skew", "2026-10-09")
SD = Entry("definition", "standard deviation", "standard deviation", "How spread out the values are.", "", "2026-10-09")


# --- base forms -------------------------------------------------------------------


@pytest.mark.parametrize(
    "word, base",
    [("sighed", "sigh"), ("ran", "run"), ("went", "go"), ("children", "child"), ("skewed", "skew"),
     ("Sighed", "sigh"), ("dog’s", "dog"), ("skew", "skew")],
)
def test_base_form(word, base):
    assert base_form(word) == base


def test_hoped_and_hopped_are_different_words():
    assert base_form("hoped") == "hope"
    assert base_form("hopped") == "hop"


def test_an_unknown_word_comes_back_lower_cased():
    assert base_form("Xyzzyed") == "xyzzyed"


# --- where it is kept --------------------------------------------------------------


def test_the_environment_variable_names_the_file(monkeypatch, tmp_path):
    monkeypatch.setenv("SENTMINE_HISTORY", str(tmp_path / "mine.jsonl"))
    assert default_history_path() == tmp_path / "mine.jsonl"


def test_on_windows_it_is_in_appdata(monkeypatch, tmp_path):
    monkeypatch.delenv("SENTMINE_HISTORY", raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert default_history_path() == tmp_path / "sentmine" / "history.jsonl"


def test_elsewhere_it_is_in_the_home_folder(monkeypatch, tmp_path):
    monkeypatch.delenv("SENTMINE_HISTORY", raising=False)
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    assert default_history_path() == tmp_path / ".local" / "share" / "sentmine" / "history.jsonl"


# --- reading and adding --------------------------------------------------------------


def test_a_missing_file_is_an_empty_history(tmp_path):
    history = History(tmp_path / "none.jsonl")
    assert (history.entries, history.problem) == ([], "")
    assert not (tmp_path / "none.jsonl").exists()


def test_first_use_creates_the_file_and_its_folder(tmp_path):
    path = tmp_path / "sentmine" / "history.jsonl"
    assert History(path).add([SIGHED, SD]) == 2
    lines = path.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["key"] for line in lines] == ["sigh", "standard deviation"]


def test_an_entry_holds_everything_and_reads_back_the_same(tmp_path):
    path = tmp_path / "history.jsonl"
    History(path).add([SIGHED])
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "kind": "word", "key": "sigh", "front": "Its owner sighed.", "back": "sighed (sigh)",
        "word": "sighed", "date": "2026-10-17",
    }
    assert History(path).entries == [SIGHED]


def test_the_same_card_is_not_added_twice(tmp_path):
    path = tmp_path / "history.jsonl"
    history = History(path)
    history.add([SKEW, SD])
    assert history.add([SKEW, SD]) == 0
    later = Entry(*SKEW.same_card, "skew", "2026-11-01")  # the same card on another day
    assert History(path).add([later]) == 0
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2


def test_an_edited_card_is_a_new_entry(tmp_path):
    history = History(tmp_path / "history.jsonl")
    history.add([SKEW])
    edited = Entry("word", "skew", SKEW.front, "skew: to distort", "skew", "2026-10-17")
    assert history.add([edited]) == 1


def test_an_unfinished_last_line_is_not_glued_to_the_new_one(tmp_path):
    path = tmp_path / "history.jsonl"
    path.write_text(json.dumps({name: getattr(SKEW, name) for name in SKEW.__dataclass_fields__}), encoding="utf-8")
    History(path).add([SIGHED])
    assert History(path).entries == [SKEW, SIGHED]


# --- finding ----------------------------------------------------------------------------


def test_finding_by_kind_and_key(tmp_path):
    history = History(tmp_path / "history.jsonl")
    history.add([SKEW, SD])
    assert history.find("word", "skew") == SKEW
    assert history.find("definition", "standard deviation") == SD
    assert history.find("definition", "skew") is None
    assert history.find("word", "variance") is None


def test_a_different_form_of_an_earlier_word_is_found(tmp_path):
    history = History(tmp_path / "history.jsonl")
    history.add([Entry("word", base_form("run"), "They run.", "run", "run", "2026-10-09")])
    assert history.find("word", base_form("ran")) is not None


def test_the_most_recent_entry_is_found(tmp_path):
    history = History(tmp_path / "history.jsonl")
    newer = Entry("word", "skew", "Polls skew young.", "skew", "skew", "2026-10-17")
    history.add([SKEW, newer])
    assert history.find("word", "skew") == newer


# --- a history that cannot be read --------------------------------------------------------


@pytest.mark.parametrize(
    "content",
    ["not json at all\n", '{"kind": "word"}\n', '{"kind": 1, "key": "a", "front": "a", "back": "a", "word": "a", "date": "x"}\n'],
)
def test_a_damaged_file_is_reported_finds_nothing_and_is_left_alone(tmp_path, content):
    path = tmp_path / "history.jsonl"
    path.write_text(content, encoding="utf-8")
    history = History(path)
    assert "could not be read" in history.problem and "line 1" in history.problem
    assert history.find("word", "skew") is None
    with pytest.raises(HistoryProblem):
        history.add([SKEW])
    assert path.read_text(encoding="utf-8") == content


def test_a_file_that_is_not_text_is_reported(tmp_path):
    path = tmp_path / "history.jsonl"
    path.write_bytes(b"\xff\xfe\x00broken")
    assert "could not be read" in History(path).problem

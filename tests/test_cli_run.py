import socket
from pathlib import Path

import pytest
from apkg_helper import read_notes

from sentmine.cli import main

DEMO_SUMMARY = (
    "Read 3 sentences, 19 words. 8 common words ignored, 5 already-known skipped, "
    "1 repeat collapsed. Wrote 5 new cards to {deck}: stubborn, refused, sighed, resilient, equally."
)


def run(capsys, *argv):
    code = main([str(a) for a in argv])
    out, err = capsys.readouterr()
    return code, out, err


def files_in(folder: Path):
    return sorted(p.name for p in folder.iterdir())


def snapshot(*paths):
    return [p.read_bytes() for p in paths]


# --- 6.2: the summary and exit 0 --------------------------------------------------------


def test_demo_run_prints_the_summary_and_exits_0(demo_files, capsys):
    deck = demo_files.folder / "new.apkg"
    code, out, err = run(capsys, demo_files.passage, "--known", demo_files.known, "--deck", deck)
    assert code == 0
    assert out.strip() == DEMO_SUMMARY.format(deck=deck)
    assert err == ""


def test_demo_deck_has_the_five_cards_in_order(demo_files, capsys):
    deck = demo_files.folder / "new.apkg"
    run(capsys, demo_files.passage, "--known", demo_files.known, "--deck", deck)
    notes, _ = read_notes(deck, demo_files.folder)
    assert [back for _guid, _front, back in notes] == ["stubborn", "refused", "sighed", "resilient", "equally"]
    assert notes[0][1] == "The <b>stubborn</b> old dog refused to move."


def test_default_deck_is_named_after_the_passage_in_the_current_folder(demo_files, capsys, monkeypatch, tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    code, out, _ = run(capsys, demo_files.passage)
    assert code == 0
    assert files_in(work) == ["passage.apkg"]
    assert "to passage.apkg:" in out


def test_singular_forms_in_the_summary(tmp_path, capsys):
    passage = tmp_path / "one.txt"
    passage.write_text("Stubborn.", encoding="utf-8")
    code, out, _ = run(capsys, passage, "--deck", tmp_path / "x.apkg")
    assert code == 0
    assert out.startswith("Read 1 sentence, 1 word. 0 common words ignored, 0 already-known skipped, 0 repeats collapsed.")
    assert "Wrote 1 new card to" in out


def test_min_len_is_used(demo_files, capsys):
    deck = demo_files.folder / "new.apkg"
    code, out, _ = run(capsys, demo_files.passage, "--min-len", "8", "--deck", deck)
    assert code == 0
    assert out.strip().endswith(": stubborn, resilient.")


def test_known_file_with_a_byte_order_mark(demo_files, capsys):
    demo_files.known.write_bytes(b"\xef\xbb\xbfdog\nold\nmove\nowner\n")
    code, out, _ = run(capsys, demo_files.passage, "--known", demo_files.known, "--deck", demo_files.folder / "n.apkg")
    assert code == 0 and "5 already-known" in out


def test_works_without_a_network(demo_files, capsys, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("the tool tried to use the network")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    code, _, _ = run(capsys, demo_files.passage, "--deck", demo_files.folder / "n.apkg")
    assert code == 0


# --- 6.3: every exit-2 case, and nothing is written -----------------------------------------


def test_missing_passage(tmp_path, capsys):
    code, out, err = run(capsys, tmp_path / "nope.txt", "--deck", tmp_path / "n.apkg")
    assert code == 2 and out == ""
    assert "cannot read the passage file" in err and "nope.txt" in err
    assert files_in(tmp_path) == []


def test_unreadable_passage_is_a_folder(tmp_path, capsys):
    folder = tmp_path / "a_folder"
    folder.mkdir()
    code, _, err = run(capsys, folder, "--deck", tmp_path / "n.apkg")
    assert code == 2 and "passage" in err
    assert files_in(tmp_path) == ["a_folder"]


def test_passage_that_is_not_utf8(tmp_path, capsys):
    passage = tmp_path / "p.txt"
    passage.write_bytes(b"caf\xe9 au lait\n")
    code, _, err = run(capsys, passage, "--deck", tmp_path / "n.apkg")
    assert code == 2 and "not valid UTF-8" in err
    assert files_in(tmp_path) == ["p.txt"]


def test_missing_known_file(demo_files, capsys):
    before = files_in(demo_files.folder)
    code, out, err = run(capsys, demo_files.passage, "--known", demo_files.folder / "nope.txt")
    assert code == 2 and out == ""
    assert "known-words file" in err
    assert files_in(demo_files.folder) == before


def test_no_new_word_prints_the_counts_but_writes_no_deck(tmp_path, capsys):
    passage = tmp_path / "p.txt"
    passage.write_text("The dog is old.", encoding="utf-8")
    known = tmp_path / "k.txt"
    known.write_text("dog\nold\n", encoding="utf-8")
    code, out, err = run(capsys, passage, "--known", known, "--deck", tmp_path / "n.apkg")
    assert code == 2
    assert out.strip() == "Read 1 sentence, 4 words. 2 common words ignored, 2 already-known skipped, 0 repeats collapsed."
    assert "Wrote" not in out
    assert "no new word remains" in err
    assert files_in(tmp_path) == ["k.txt", "p.txt"]


def test_empty_passage_has_no_new_word(tmp_path, capsys):
    passage = tmp_path / "p.txt"
    passage.write_text("", encoding="utf-8")
    code, out, err = run(capsys, passage, "--deck", tmp_path / "n.apkg")
    assert code == 2 and "no new word remains" in err
    assert out.startswith("Read 0 sentences, 0 words.")
    assert files_in(tmp_path) == ["p.txt"]


def test_deck_exists_without_force(demo_files, capsys):
    deck = demo_files.folder / "new.apkg"
    deck.write_bytes(b"precious")
    code, out, err = run(capsys, demo_files.passage, "--deck", deck)
    assert code == 2 and out == ""
    assert "already exists" in err and "--force" in err
    assert deck.read_bytes() == b"precious"
    assert files_in(demo_files.folder) == ["known.txt", "new.apkg", "passage.txt"]


def test_deck_folder_does_not_exist(demo_files, capsys):
    before = files_in(demo_files.folder)
    code, out, err = run(capsys, demo_files.passage, "--deck", demo_files.folder / "missing" / "n.apkg")
    assert code == 2 and out == ""
    assert "cannot write the deck file" in err
    assert files_in(demo_files.folder) == before


def test_deck_path_is_the_passage_itself(demo_files, capsys):
    original = demo_files.passage.read_bytes()
    code, _, err = run(capsys, demo_files.passage, "--deck", demo_files.passage, "--force")
    assert code == 2 and "is an input file" in err
    assert demo_files.passage.read_bytes() == original


def test_deck_path_is_the_known_file(demo_files, capsys):
    original = demo_files.known.read_bytes()
    code, _, err = run(capsys, demo_files.passage, "--known", demo_files.known, "--deck", demo_files.known, "--force")
    assert code == 2 and "is an input file" in err
    assert demo_files.known.read_bytes() == original


# --- 6.4: input files are never modified; --force replaces --------------------------------------


def test_input_files_are_unchanged_after_a_successful_run(demo_files, capsys):
    before = snapshot(demo_files.passage, demo_files.known)
    code, _, _ = run(capsys, demo_files.passage, "--known", demo_files.known, "--deck", demo_files.folder / "n.apkg")
    assert code == 0
    assert snapshot(demo_files.passage, demo_files.known) == before


def test_input_files_are_unchanged_when_the_deck_cannot_be_written(demo_files, capsys):
    before = snapshot(demo_files.passage, demo_files.known)
    bad_deck = demo_files.folder / "missing" / "n.apkg"
    code, _, _ = run(capsys, demo_files.passage, "--known", demo_files.known, "--deck", bad_deck)
    assert code == 2
    assert snapshot(demo_files.passage, demo_files.known) == before


def test_input_files_are_unchanged_when_no_new_word_remains(demo_files, capsys):
    before = snapshot(demo_files.passage, demo_files.known)
    code, _, _ = run(capsys, demo_files.passage, "--known", demo_files.known, "--min-len", "50")
    assert code == 2
    assert snapshot(demo_files.passage, demo_files.known) == before


def test_input_files_are_unchanged_when_the_deck_exists(demo_files, capsys):
    deck = demo_files.folder / "new.apkg"
    deck.write_bytes(b"x")
    before = snapshot(demo_files.passage, demo_files.known)
    code, _, _ = run(capsys, demo_files.passage, "--known", demo_files.known, "--deck", deck)
    assert code == 2
    assert snapshot(demo_files.passage, demo_files.known) == before


def test_input_files_are_unchanged_when_a_file_is_missing(demo_files, capsys):
    before = snapshot(demo_files.passage, demo_files.known)
    code, _, _ = run(capsys, demo_files.folder / "nope.txt", "--known", demo_files.known)
    assert code == 2
    assert snapshot(demo_files.passage, demo_files.known) == before


def test_force_replaces_an_existing_deck(demo_files, capsys):
    deck = demo_files.folder / "new.apkg"
    deck.write_bytes(b"old contents")
    before = snapshot(demo_files.passage, demo_files.known)
    code, out, _ = run(capsys, demo_files.passage, "--known", demo_files.known, "--deck", deck, "--force")
    assert code == 0 and "Wrote 5 new cards" in out
    work = demo_files.folder / "unpacked"
    work.mkdir()
    notes, _ = read_notes(deck, work)
    assert len(notes) == 5
    assert snapshot(demo_files.passage, demo_files.known) == before
    assert files_in(demo_files.folder) == ["known.txt", "new.apkg", "passage.txt", "unpacked"]

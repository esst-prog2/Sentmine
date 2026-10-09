from pathlib import Path

import pytest

from sentmine.cli import build_parser, deck_path, main


def parse(*argv):
    return build_parser().parse_args(list(argv))


def test_defaults():
    args = parse("passage.txt")
    assert args.passage == "passage.txt"
    assert args.known is None
    assert args.deck is None
    assert args.min_len == 3
    assert args.force is False


def test_default_deck_name_is_the_passage_name_with_apkg():
    assert deck_path(parse("passage.txt")) == Path("passage.apkg")


def test_default_deck_is_in_the_current_folder_not_next_to_the_passage():
    assert deck_path(parse("some/folder/article.txt")) == Path("article.apkg")


def test_deck_option_wins():
    assert deck_path(parse("passage.txt", "--deck", "out/new.apkg")) == Path("out/new.apkg")


def test_all_options():
    args = parse("p.txt", "--known", "k.txt", "--deck", "d.apkg", "--min-len", "5", "--force")
    assert (args.known, args.deck, args.min_len, args.force) == ("k.txt", "d.apkg", 5, True)


@pytest.mark.parametrize("value", ["abc", "0", "-2", "1.5", ""])
def test_invalid_min_len_exits_with_2(value, capsys):
    with pytest.raises(SystemExit) as stop:
        main(["passage.txt", "--min-len", value])
    assert stop.value.code == 2
    assert "--min-len" in capsys.readouterr().err


def test_min_len_of_one_is_allowed():
    assert parse("passage.txt", "--min-len", "1").min_len == 1


def test_there_is_no_report_option(capsys):
    with pytest.raises(SystemExit) as stop:
        main(["passage.txt", "--report", "clean.html"])
    assert stop.value.code == 2


def test_no_arguments_starts_the_reading_app(monkeypatch):
    started = []
    monkeypatch.setattr("sentmine.app.serve", lambda: started.append(True) or 0)
    assert main([]) == 0
    assert started == [True]


def test_an_option_without_a_passage_exits_with_2(monkeypatch, capsys):
    monkeypatch.setattr("sentmine.app.serve", lambda: pytest.fail("the reading app must not start"))
    with pytest.raises(SystemExit) as stop:
        main(["--force"])
    assert stop.value.code == 2

"""Command-line entry point."""

import argparse
import sys
from pathlib import Path

from sentmine.analyse import Analysis, analyse
from sentmine.deck import write_deck

DEFAULT_MIN_LEN = 3
EXIT_OK = 0
EXIT_PROBLEM = 2  # nothing was written; a message on stderr names the problem


def _min_len(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a whole number") from None
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentmine",
        description="Make an Anki deck of the new words in an English passage, "
        "each word inside the sentence it appeared in. "
        "Run with no arguments to open the reading app in the browser instead.",
    )
    parser.add_argument("passage", help="plain-text file with the passage")
    parser.add_argument(
        "--known",
        metavar="FILE",
        help="file of words you already know, one per line",
    )
    parser.add_argument(
        "--deck",
        metavar="FILE",
        help="where to write the deck (default: the passage name with .apkg, in the current folder)",
    )
    parser.add_argument(
        "--min-len",
        type=_min_len,
        default=DEFAULT_MIN_LEN,
        metavar="N",
        help=f"ignore words shorter than N letters (default: {DEFAULT_MIN_LEN})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace the deck file if it already exists",
    )
    return parser


def deck_path(args: argparse.Namespace) -> Path:
    """The deck file to write: --deck, or the passage name with .apkg in the current folder."""
    if args.deck:
        return Path(args.deck)
    return Path(Path(args.passage).stem + ".apkg")


class InputProblem(Exception):
    """An input file could not be read."""


def _read_text(path: Path, what: str) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise InputProblem(f"the {what} file '{path}' is not valid UTF-8 text") from None
    except OSError as error:
        raise InputProblem(f"cannot read the {what} file '{path}': {error.strerror or error}") from None


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def counts_summary(result: Analysis) -> str:
    return (
        f"Read {_count(result.sentences, 'sentence')}, {_count(result.words, 'word')}. "
        f"{_count(result.common, 'common word')} ignored, "
        f"{result.known} already-known skipped, "
        f"{_count(result.repeats, 'repeat')} collapsed."
    )


def summary(result: Analysis, deck: Path) -> str:
    words = ", ".join(card.word for card in result.cards)
    return f"{counts_summary(result)} Wrote {_count(len(result.cards), 'new card')} to {deck}: {words}."


def _fail(message: str) -> int:
    print(f"sentmine: error: {message}", file=sys.stderr)
    return EXIT_PROBLEM


def _same_file(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return False


def _tolerate_any_character() -> None:
    """A console that cannot show a character should print '?', not crash."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _tolerate_any_character()
    if not (sys.argv[1:] if argv is None else argv):
        from sentmine.app import serve  # no arguments at all: the reading app

        return serve()
    args = build_parser().parse_args(argv)  # exits with 2 on invalid arguments
    passage = Path(args.passage)
    known = Path(args.known) if args.known else None
    deck = deck_path(args)

    try:
        text = _read_text(passage, "passage")
        known_words = _read_text(known, "known-words").splitlines() if known else []
    except InputProblem as problem:
        return _fail(str(problem))

    result = analyse(text, known_words, args.min_len)
    if not result.cards:
        print(counts_summary(result))
        return _fail("no new word remains: every word is common, too short or already known")

    for original in (passage, known):
        if original is not None and _same_file(deck, original):
            return _fail(f"the deck file '{deck}' is an input file; choose another --deck")
    if deck.exists() and not args.force:
        return _fail(f"the deck file '{deck}' already exists; use --force to replace it")
    try:
        write_deck(result.cards, deck)
    except OSError as error:
        return _fail(f"cannot write the deck file '{deck}': {error.strerror or error}")

    print(summary(result, deck))
    return EXIT_OK

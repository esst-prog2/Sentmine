"""A remembered card, and the reader for the old history file (history.jsonl).

The memory itself is now a SQLite database (memory.py). This module only describes a
card and reads the JSON Lines file that the app used before, so its cards can be moved
into the database once.
"""

import json
from dataclasses import dataclass
from pathlib import Path

FIELDS = ("kind", "key", "front", "back", "word", "date")


class HistoryProblem(Exception):
    """The old history file cannot be read; the message says which file and why."""


@dataclass(frozen=True)
class Entry:
    kind: str  # "word" or "definition"
    key: str  # the base form of the word, or the term in lower case with single spaces
    front: str  # as downloaded
    back: str  # as downloaded
    word: str  # word cards: the word as clicked; "" for a definition card
    date: str  # the day of the download, YYYY-MM-DD


def read_history_file(path: Path) -> list[Entry]:
    """Every card in an old history file, in order. A missing file has none."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except (OSError, UnicodeDecodeError) as error:
        raise HistoryProblem(f"The old card history '{path}' could not be read ({error}).") from None
    entries = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            values = [data[name] for name in FIELDS]
            if not all(isinstance(value, str) for value in values):
                raise TypeError
        except (ValueError, KeyError, TypeError):
            raise HistoryProblem(
                f"The old card history '{path}' could not be read: line {number} is not a card."
            ) from None
        entries.append(Entry(*values))
    return entries

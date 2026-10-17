"""The history of downloaded cards: one JSON object per line, in the reader's own user folder."""

import json
import os
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

FIELDS = ("kind", "key", "front", "back", "word", "date")


class HistoryProblem(Exception):
    """The history file cannot be read or written; the message says which file and why."""


@dataclass(frozen=True)
class Entry:
    kind: str  # "word" or "definition"
    key: str  # the base form of the word, or the term in lower case with single spaces
    front: str  # as downloaded
    back: str  # as downloaded
    word: str  # word cards: the word as clicked; "" for a definition card
    date: str  # the day of the download, YYYY-MM-DD

    @property
    def same_card(self) -> tuple[str, str, str, str]:
        """What makes two entries the same card; the date and the clicked form do not."""
        return (self.kind, self.key, self.front, self.back)


def default_history_path() -> Path:
    """SENTMINE_HISTORY if set; otherwise %APPDATA%\\sentmine on Windows, ~/.local/share/sentmine elsewhere."""
    named = os.environ.get("SENTMINE_HISTORY")
    if named:
        return Path(named)
    appdata = os.environ.get("APPDATA")
    folder = Path(appdata) if appdata else Path.home() / ".local" / "share"
    return folder / "sentmine" / "history.jsonl"


class History:
    """The history, read once when it is opened. A file that cannot be read gives a history
    that finds nothing, adds nothing, never touches the file, and says why in `problem`."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.entries: list[Entry] = []
        self.problem = ""
        try:
            self.entries = self._read()
        except HistoryProblem as error:
            self.problem = str(error)

    def _read(self) -> list[Entry]:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return []
        except (OSError, UnicodeDecodeError) as error:
            raise HistoryProblem(f"The card history '{self.path}' could not be read ({error}).") from None
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
                    f"The card history '{self.path}' could not be read: line {number} is not a card."
                ) from None
            entries.append(Entry(*values))
        return entries

    def find(self, kind: str, key: str) -> Entry | None:
        """The most recent entry of this kind and key, or None."""
        for entry in reversed(self.entries):
            if entry.kind == kind and entry.key == key:
                return entry
        return None

    def add(self, entries: Iterable[Entry]) -> int:
        """Append the entries that are not already in the history; returns how many were added."""
        if self.problem:
            raise HistoryProblem(self.problem)
        seen = {entry.same_card for entry in self.entries}
        new = []
        for entry in entries:
            if entry.same_card not in seen:
                seen.add(entry.same_card)
                new.append(entry)
        if not new:
            return 0
        lines = "".join(json.dumps(asdict(entry), ensure_ascii=False) + "\n" for entry in new)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists() and self.path.stat().st_size > 0:
                with self.path.open("rb") as existing:
                    existing.seek(-1, os.SEEK_END)
                    if existing.read(1) != b"\n":
                        lines = "\n" + lines  # never glue a new entry onto an unfinished line
            with self.path.open("a", encoding="utf-8", newline="\n") as file:
                file.write(lines)
        except OSError as error:
            raise HistoryProblem(f"The cards could not be added to the history '{self.path}' ({error}).") from None
        self.entries.extend(new)
        return len(new)

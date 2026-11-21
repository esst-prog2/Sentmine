"""The memory of every card the reader has downloaded: a SQLite database in the reader's own folder."""

import os
import shutil
import sqlite3
from collections.abc import Iterable, Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from sentmine.history import Entry, HistoryProblem, read_history_file

DATABASE_NAME = "cards.db"
OLD_HISTORY_NAME = "history.jsonl"  # the file remember-cards wrote before the database existed
SHOWN_AT_MOST = 200
MONTHS_SHOWN = 6

# Each step brings the layout up by one version; it runs in one transaction with its version number.
SCHEMA_VERSION = 4
_CREATE_TABLE = """
    CREATE TABLE cards (
        id INTEGER PRIMARY KEY,
        kind TEXT NOT NULL CHECK (kind IN ('word', 'definition')),
        key TEXT NOT NULL,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        word TEXT NOT NULL DEFAULT '',
        made_on TEXT NOT NULL,
        UNIQUE (kind, key, front, back)
    )
"""
_CREATE_INDEX = "CREATE INDEX cards_by_key ON cards (kind, key)"
# Layout 3: each text a card's word or term was met in; `made` marks the text the card was made from.
_CREATE_MEETINGS = """
    CREATE TABLE meetings (
        kind TEXT NOT NULL,
        key TEXT NOT NULL,
        text_id TEXT NOT NULL,
        made INTEGER NOT NULL DEFAULT 0,
        day TEXT NOT NULL,
        PRIMARY KEY (kind, key, text_id)
    )
"""
# Layout 4: where a card came from (a PDF's name or a web page's title, its address, the page in it).
_SOURCE_COLUMNS = ("source", "source_url", "source_place")
_INSERT = ("INSERT OR IGNORE INTO cards (kind, key, front, back, word, made_on, source, source_url, source_place) "
           "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
_COLUMNS = "id, kind, key, front, back, word, made_on, source, source_url, source_place"
SOURCES_SHOWN = 5


class MemoryProblem(Exception):
    """The memory cannot be opened, read or changed; the message says which file and why."""


@dataclass(frozen=True)
class RememberedCard:
    id: int
    entry: Entry


def default_folder() -> Path:
    """%APPDATA%\\sentmine on Windows, ~/.local/share/sentmine elsewhere."""
    appdata = os.environ.get("APPDATA")
    return (Path(appdata) if appdata else Path.home() / ".local" / "share") / "sentmine"


def default_memory_path() -> Path:
    """SENTMINE_DATABASE if set, otherwise cards.db in the default folder."""
    named = os.environ.get("SENTMINE_DATABASE")
    return Path(named) if named else default_folder() / DATABASE_NAME


class CardMemory:
    """The reader's remembered cards. A database that cannot be opened gives a memory that
    finds nothing, refuses changes, never touches the file, and says why in `problem`."""

    def __init__(self, path: Path, old_history: Path | None = None) -> None:
        self.path = Path(path)
        self.old_history = Path(old_history) if old_history is not None else self.path.with_name(OLD_HISTORY_NAME)
        self.problem = ""
        self.notice = ""  # what opening did, for the terminal: e.g. cards moved from the old file
        try:
            self._open()
        except MemoryProblem as error:
            self.problem = str(error)

    # --- opening and migrating ----------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        try:
            return sqlite3.connect(self.path, isolation_level=None)  # transactions are begun by hand
        except sqlite3.Error as error:
            raise MemoryProblem(f"The card memory '{self.path}' could not be opened ({error}).") from None

    def _open(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise MemoryProblem(f"The folder for the card memory '{self.path}' could not be made ({error}).") from None
        with closing(self._connect()) as db:
            try:
                version = _version(db)
                if version > SCHEMA_VERSION:
                    raise MemoryProblem(
                        f"The card memory '{self.path}' was made by a newer version of sentmine "
                        f"(layout {version}; this version knows up to {SCHEMA_VERSION})."
                    )
                if version < 1:
                    with _transaction(db):
                        if _version(db) < 1:  # another copy of the app may have just done it
                            db.execute(_CREATE_TABLE)
                            db.execute(_CREATE_INDEX)
                            db.execute("PRAGMA user_version = 1")
                if version < 2:
                    self._move_old_history(db)
                if _version(db) < 3:
                    with _transaction(db):
                        if _version(db) < 3:
                            db.execute(_CREATE_MEETINGS)
                            db.execute("PRAGMA user_version = 3")
                if _version(db) < 4:
                    self._keep_a_copy(db, 4)
                    with _transaction(db):
                        if _version(db) < 4:
                            there = {row[1] for row in db.execute("PRAGMA table_info(cards)")}
                            for column in _SOURCE_COLUMNS:
                                if column not in there:
                                    db.execute(f"ALTER TABLE cards ADD COLUMN {column} TEXT NOT NULL DEFAULT ''")
                            db.execute("PRAGMA user_version = 4")
            except sqlite3.DatabaseError as error:
                raise MemoryProblem(f"The card memory '{self.path}' could not be opened ({error}).") from None

    def _keep_a_copy(self, db: sqlite3.Connection, layout: int) -> None:
        """Before the layout changes, a copy of a memory that has cards, beside it; made once."""
        copy = self.path.with_name(f"{self.path.name}.before-layout-{layout}")
        try:
            if not copy.exists() and db.execute("SELECT COUNT(*) FROM cards").fetchone()[0]:
                shutil.copy2(self.path, copy)
        except OSError:
            pass  # the change itself is one transaction; the copy is an extra

    def _move_old_history(self, db: sqlite3.Connection) -> None:
        """Layout 2: copy the old history file's cards in, once. The old file is never changed."""
        try:
            entries = read_history_file(self.old_history)
        except HistoryProblem as error:
            raise MemoryProblem(f"{error} Its cards were not moved into the memory; sentmine will try again next time.") from None
        moved = 0
        with _transaction(db):
            if _version(db) < 2:
                before = db.total_changes
                # the table as layout 1 made it: the source columns come with layout 4
                db.executemany(
                    "INSERT OR IGNORE INTO cards (kind, key, front, back, word, made_on) VALUES (?, ?, ?, ?, ?, ?)",
                    [_row(entry)[:6] for entry in entries],
                )
                moved = db.total_changes - before
                db.execute("PRAGMA user_version = 2")
        if entries:
            self.notice = f"moved {moved} cards from the old history file '{self.old_history}' into the memory"

    # --- what the reading page needs ------------------------------------------------------

    def find(self, kind: str, key: str) -> Entry | None:
        """The most recent remembered card of this kind and key, or None."""
        if self.problem:
            return None
        row = self._query(
            f"SELECT {_COLUMNS} FROM cards WHERE kind = ? AND key = ? ORDER BY made_on DESC, id DESC LIMIT 1",
            (kind, key),
        )
        return _card(row[0]).entry if row else None

    def word_cards(self) -> dict[str, Entry]:
        """The latest word card for each base form, by base form; empty when the memory cannot be read."""
        return self._latest("word")

    def term_cards(self) -> dict[str, Entry]:
        """The latest definition card for each term, by term (lower case, single spaces); empty when unreadable."""
        return self._latest("definition")

    def _latest(self, kind: str) -> dict[str, Entry]:
        if self.problem:
            return {}
        try:
            rows = self._query(f"SELECT {_COLUMNS} FROM cards WHERE kind = ? ORDER BY made_on, id", (kind,))
        except MemoryProblem:
            return {}
        return {entry.key: entry for entry in (_card(row).entry for row in rows)}

    def add(self, entries: Iterable[Entry]) -> int:
        """Remember the cards that are not remembered yet; returns how many were new."""
        self._usable()
        with closing(self._connect()) as db:
            try:
                with _transaction(db):
                    before = db.total_changes
                    db.executemany(_INSERT, [_row(entry) for entry in entries])
                    return db.total_changes - before
            except sqlite3.Error as error:
                raise MemoryProblem(f"The cards could not be added to the card memory '{self.path}' ({error}).") from None

    def meet(self, cards: Iterable[tuple[str, str]], text_id: str, day: str) -> None:
        """Record that these cards (kind, key) were met in a text; once per text, the first day kept."""
        self._write(
            "INSERT OR IGNORE INTO meetings (kind, key, text_id, made, day) VALUES (?, ?, ?, 0, ?)",
            [(kind, key, text_id, day) for kind, key in cards],
            "The cards met in this text could not be recorded",
        )

    def made_from(self, cards: Iterable[tuple[str, str]], text_id: str, day: str) -> None:
        """Record the text these cards (kind, key) were made from, which does not count as meeting them again."""
        self._write(
            "INSERT INTO meetings (kind, key, text_id, made, day) VALUES (?, ?, ?, 1, ?) "
            "ON CONFLICT (kind, key, text_id) DO UPDATE SET made = 1",
            [(kind, key, text_id, day) for kind, key in cards],
            "The text these cards were made from could not be recorded",
        )

    def met_again(self) -> dict[tuple[str, str], tuple[int, str]]:
        """For each card (kind, key) met again: in how many texts, and the last day; empty when unreadable."""
        if self.problem:
            return {}
        try:
            rows = self._query("SELECT kind, key, COUNT(*), MAX(day) FROM meetings WHERE made = 0 GROUP BY kind, key", ())
        except MemoryProblem:
            return {}
        return {(kind, key): (count, last) for kind, key, count, last in rows}

    def _write(self, sql: str, rows: list[tuple], failed: str) -> None:
        self._usable()
        if not rows:
            return
        with closing(self._connect()) as db:
            try:
                with _transaction(db):
                    db.executemany(sql, rows)
            except sqlite3.Error as error:
                raise MemoryProblem(f"{failed} in the card memory '{self.path}' ({error}).") from None

    # --- what the My cards page needs -----------------------------------------------------

    def search(self, text: str = "", limit: int = SHOWN_AT_MOST) -> tuple[list[RememberedCard], int]:
        """The cards whose word, key, front or back contains `text` (any case), newest first,
        at most `limit` of them, and how many match in all."""
        if self.problem:
            return [], 0
        where, values = "", ()
        if text.strip():
            pattern = "%" + text.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
            where = " WHERE " + " OR ".join(f"{column} LIKE ? ESCAPE '\\'" for column in ("word", "key", "front", "back"))
            values = (pattern,) * 4
        total = self._query("SELECT COUNT(*) FROM cards" + where, values)[0][0]
        rows = self._query(f"SELECT {_COLUMNS} FROM cards{where} ORDER BY made_on DESC, id DESC LIMIT ?", (*values, limit))
        return [_card(row) for row in rows], total

    def progress(self, today: date | None = None) -> dict:
        """Cards in total, by kind, this week (from Monday), and in each of the last six months."""
        today = today or date.today()
        if self.problem:
            return {"total": 0, "words": 0, "definitions": 0, "this_week": 0, "months": [], "sources": []}
        monday = (today - timedelta(days=today.weekday())).isoformat()
        total, words, this_week = self._query(
            "SELECT COUNT(*), COALESCE(SUM(kind = 'word'), 0), COALESCE(SUM(made_on >= ?), 0) FROM cards", (monday,)
        )[0]
        months = _last_months(today, MONTHS_SHOWN)
        counted = dict(self._query(
            "SELECT substr(made_on, 1, 7), COUNT(*) FROM cards WHERE made_on >= ? GROUP BY 1", (months[0] + "-01",)
        ))
        return {
            "total": total,
            "words": words,
            "definitions": total - words,
            "this_week": this_week,
            "months": [{"month": month, "cards": counted.get(month, 0)} for month in months],
            # the books and pages most cards came from
            "sources": [{"source": source, "cards": cards} for source, cards in self._query(
                "SELECT source, COUNT(*) FROM cards WHERE source != '' GROUP BY source ORDER BY 2 DESC, 1 LIMIT ?",
                (SOURCES_SHOWN,))],
        }

    def delete(self, card_id: int) -> None:
        """Forget one remembered card. It is not undone; the page asks first."""
        self._usable()
        with closing(self._connect()) as db:
            try:
                with _transaction(db):
                    found = db.execute("SELECT kind, key FROM cards WHERE id = ?", (card_id,)).fetchone()
                    gone = db.execute("DELETE FROM cards WHERE id = ?", (card_id,)).rowcount
                    if found and not db.execute("SELECT 1 FROM cards WHERE kind = ? AND key = ?", found).fetchone():
                        db.execute("DELETE FROM meetings WHERE kind = ? AND key = ?", found)  # the last card for it
            except sqlite3.Error as error:
                raise MemoryProblem(f"The card could not be deleted from the card memory '{self.path}' ({error}).") from None
        if not gone:
            raise MemoryProblem("That card is not in the memory any more.")

    def count(self) -> int:
        return self.search(limit=0)[1]

    @property
    def entries(self) -> list[Entry]:
        """Every remembered card, oldest first."""
        if self.problem:
            return []
        return [_card(row).entry for row in self._query(f"SELECT {_COLUMNS} FROM cards ORDER BY id", ())]

    # --- helpers --------------------------------------------------------------------------

    def _usable(self) -> None:
        if self.problem:
            raise MemoryProblem(self.problem)

    def _query(self, sql: str, values: tuple) -> list[tuple]:
        with closing(self._connect()) as db:
            try:
                return db.execute(sql, values).fetchall()
            except sqlite3.Error as error:
                raise MemoryProblem(f"The card memory '{self.path}' could not be read ({error}).") from None


@contextmanager
def _transaction(db: sqlite3.Connection) -> Iterator[None]:
    """Everything inside happens completely or not at all."""
    db.execute("BEGIN IMMEDIATE")
    try:
        yield
    except BaseException:
        db.execute("ROLLBACK")
        raise
    db.execute("COMMIT")


def _version(db: sqlite3.Connection) -> int:
    return db.execute("PRAGMA user_version").fetchone()[0]


def _row(entry: Entry) -> tuple:
    return (entry.kind, entry.key, entry.front, entry.back, entry.word, entry.date,
            entry.source, entry.source_url, entry.source_place)


def _card(row: tuple) -> RememberedCard:
    card_id, kind, key, front, back, word, made_on, source, source_url, source_place = row
    return RememberedCard(card_id, Entry(kind, key, front, back, word, made_on, source, source_url, source_place))


def _last_months(today: date, count: int) -> list[str]:
    """`YYYY-MM` of the last `count` months, oldest first, ending with this month."""
    year, month = today.year, today.month
    months = []
    for _ in range(count):
        months.append(f"{year:04d}-{month:02d}")
        year, month = (year, month - 1) if month > 1 else (year - 1, 12)
    return months[::-1]

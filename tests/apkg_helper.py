"""Read an .apkg back: it is a zip that holds an SQLite database."""

import sqlite3
import zipfile


def read_notes(apkg, work_folder):
    """([(guid, front, back), ...] in note order, the deck json) of an .apkg file."""
    with zipfile.ZipFile(apkg) as z:
        assert "collection.anki2" in z.namelist()
        z.extract("collection.anki2", work_folder)
    db = sqlite3.connect(work_folder / "collection.anki2")
    try:
        rows = db.execute("select guid, flds from notes order by id").fetchall()
        decks = db.execute("select decks from col").fetchone()[0]
    finally:
        db.close()
    return [(guid, *flds.split("\x1f")) for guid, flds in rows], decks

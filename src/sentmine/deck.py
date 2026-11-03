"""Make the cards and write them as an Anki .apkg deck."""

import html
import os
import zlib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import genanki

from sentmine.analyse import Card
from sentmine.words import find_words

# Anki tells note types apart by id, so these are fixed for good.
MODEL_ID = 1766200417
CLOZE_MODEL_ID = 1766200418

MODEL = genanki.Model(
    MODEL_ID,
    "sentmine: word in its sentence",
    fields=[{"name": "Front"}, {"name": "Back"}],
    templates=[
        {
            "name": "Word in sentence",
            "qfmt": "{{Front}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Back}}',
        }
    ],
)


CLOZE_MODEL = genanki.Model(
    CLOZE_MODEL_ID,
    "sentmine: cloze",
    fields=[{"name": "Text"}, {"name": "Back Extra"}],
    templates=[
        {
            "name": "Cloze",
            "qfmt": "{{cloze:Text}}",
            "afmt": "{{cloze:Text}}<br>{{Back Extra}}",
        }
    ],
    model_type=genanki.Model.CLOZE,
)


@dataclass(frozen=True)
class Note:
    """The fields of one note, as HTML, and which sentmine note type it uses."""

    fields: tuple[str, ...]
    cloze: bool = False

    @property
    def model(self) -> genanki.Model:
        return CLOZE_MODEL if self.cloze else MODEL


def as_note(note: "Note | tuple[str, str]") -> Note:
    """A (front, back) pair is a note of the first note type."""
    return note if isinstance(note, Note) else Note(tuple(note))


class _Note(genanki.Note):
    """A note whose id comes from its text, so importing it twice adds nothing new."""

    @property
    def guid(self) -> str:
        return genanki.guid_for(*self.fields)


def card_front(sentence: str, word: str) -> str:
    """The sentence with < > & escaped and every whole-word `word` in bold, case kept."""
    parts: list[str] = []
    position = 0
    for found in find_words(sentence):
        if found.ignored or found.text != word:
            continue
        parts.append(html.escape(sentence[position : found.start], quote=False))
        parts.append("<b>" + html.escape(sentence[found.start : found.end], quote=False) + "</b>")
        position = found.end
    parts.append(html.escape(sentence[position:], quote=False))
    return "".join(parts)


def card_back(word: str) -> str:
    return word.lower()


def deck_id_for(name: str) -> int:
    """A stable deck id from the deck name, so a re-import lands in the same deck."""
    return (1 << 30) + zlib.crc32(name.encode("utf-8")) % (1 << 30)


def write_deck(cards: Sequence[Card], path: Path) -> None:
    """Write one word card per card to `path`."""
    write_notes([(card_front(card.sentence, card.word), card_back(card.word)) for card in cards], path)


def write_notes(notes: Sequence[Note | tuple[str, str]], path: Path) -> None:
    """Write notes, or (front, back) pairs of HTML, to `path`; the file appears only once it is complete."""
    path = Path(path)
    deck = genanki.Deck(deck_id_for(path.stem), path.stem)
    for note in map(as_note, notes):
        deck.add_note(_Note(model=note.model, fields=list(note.fields)))
    partial = path.with_name(path.name + ".part")
    try:
        genanki.Package(deck).write_to_file(str(partial))
        os.replace(partial, path)
    finally:
        if partial.exists():
            partial.unlink()

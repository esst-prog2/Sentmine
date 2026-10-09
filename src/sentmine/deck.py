"""Make the cards and write them as an Anki .apkg deck."""

import html
import os
import zlib
from collections.abc import Sequence
from pathlib import Path

import genanki

from sentmine.analyse import Card
from sentmine.words import find_words

# Anki tells note types apart by id, so this one is fixed for good.
MODEL_ID = 1766200417

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


class _Note(genanki.Note):
    """A note whose id comes from its text, so importing it twice adds nothing new."""

    @property
    def guid(self) -> str:
        return genanki.guid_for(self.fields[0], self.fields[1])


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


def write_notes(notes: Sequence[tuple[str, str]], path: Path) -> None:
    """Write (front, back) pairs of HTML to `path`; the file appears only once it is complete."""
    path = Path(path)
    deck = genanki.Deck(deck_id_for(path.stem), path.stem)
    for front, back in notes:
        deck.add_note(_Note(model=MODEL, fields=[front, back]))
    partial = path.with_name(path.name + ".part")
    try:
        genanki.Package(deck).write_to_file(str(partial))
        os.replace(partial, path)
    finally:
        if partial.exists():
            partial.unlink()

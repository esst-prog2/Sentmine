"""The reading session behind the page: one pasted text and the cards the reader made from it."""

import html
import re
from dataclasses import dataclass
from pathlib import Path

from sentmine.deck import card_back, card_front, write_notes
from sentmine.sentences import split_sentences
from sentmine.stem import stem
from sentmine.words import Word, find_words

WORD = "word"
DEFINITION = "definition"

ADDED = "added"
REMOVED = "removed"
DUPLICATE = "duplicate"

_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
_LINE_BREAK = re.compile(r"\s*\n\s*")
_SPACES = re.compile(r"[^\S\n]+")  # spaces and tabs, but not line breaks
_NEWLINES = re.compile(r"\s*\n\s*")


class Problem(ValueError):
    """Something the reader asked for cannot be done; the message says why."""


@dataclass
class Flashcard:
    id: int
    kind: str  # WORD or DEFINITION
    front: str  # plain text: the sentence, or the term
    back: str  # plain text: the word, or the marked passage
    key: str  # two cards with the same key are the same card
    word: str = ""  # word cards: the word shown in bold on the front
    place: tuple[int, int] | None = None  # word cards: the sentence and word that were clicked

    @property
    def front_html(self) -> str:
        if self.kind == WORD:
            return card_front(self.front, self.word).replace("\n", "<br>")
        return _plain_html(self.front)

    @property
    def back_html(self) -> str:
        return _plain_html(self.back)


def _plain_html(text: str) -> str:
    return html.escape(text, quote=False).replace("\n", "<br>")


def tidy(text: str) -> str:
    """Paragraphs separated by one blank line; a line break inside a paragraph becomes a space."""
    paragraphs = []
    for paragraph in _PARAGRAPH_BREAK.split(text.replace("\r\n", "\n").replace("\r", "\n")):
        paragraph = _SPACES.sub(" ", _LINE_BREAK.sub(" ", paragraph.strip()))
        if paragraph:
            paragraphs.append(paragraph)
    return "\n\n".join(paragraphs)


def tidy_selection(text: str) -> str:
    """A selection from the page: paragraph breaks kept, every other run of spaces made one space."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return _NEWLINES.sub("\n\n", _SPACES.sub(" ", text))


def clickable_words(sentence: str) -> list[Word]:
    """The words of a sentence the reader can pick; a token with a digit is not one."""
    return [word for word in find_words(sentence) if not word.ignored]


class Session:
    """One text and its cards, kept in memory for one reader."""

    def __init__(self) -> None:
        self.paragraphs: list[list[str]] = []  # each paragraph is a list of sentences
        self.cards: list[Flashcard] = []
        self._next_id = 1

    @property
    def sentences(self) -> list[str]:
        return [sentence for paragraph in self.paragraphs for sentence in paragraph]

    def load(self, text: str) -> None:
        """Replace the text, and with it the cards made from the old one."""
        tidied = tidy(text)
        if not tidied:
            raise Problem("There is no text to read: paste a text first.")
        self.paragraphs = [split_sentences(paragraph) for paragraph in tidied.split("\n\n")]
        self.cards = []

    def layout(self) -> list[list[dict]]:
        """The text as the page draws it: paragraphs of sentences, each cut into words and the text between."""
        picked = {card.place for card in self.cards if card.place is not None}
        paragraphs = []
        number = 0
        for paragraph in self.paragraphs:
            drawn = []
            for sentence in paragraph:
                pieces = []
                position = 0
                for index, word in enumerate(clickable_words(sentence)):
                    if word.start > position:
                        pieces.append({"text": sentence[position : word.start]})
                    pieces.append(
                        {
                            "text": sentence[word.start : word.end],
                            "word": index,
                            "picked": (number, index) in picked,
                        }
                    )
                    position = word.end
                if position < len(sentence):
                    pieces.append({"text": sentence[position:]})
                drawn.append({"sentence": number, "pieces": pieces})
                number += 1
            paragraphs.append(drawn)
        return paragraphs

    def pick_word(self, sentence: int, word: int) -> tuple[str, Flashcard]:
        """A click on a word: make its card, or remove the card this very word made."""
        sentences = self.sentences
        if not 0 <= sentence < len(sentences):
            raise Problem("That sentence is not in the text.")
        words = clickable_words(sentences[sentence])
        if not 0 <= word < len(words):
            raise Problem("That word is not in the sentence.")
        text = words[word].text
        key = WORD + ":" + stem(text)
        existing = self._card_with_key(key)
        if existing is None:
            return ADDED, self._add(
                Flashcard(0, WORD, sentences[sentence], card_back(text), key, word=text, place=(sentence, word))
            )
        if existing.place == (sentence, word):
            self.cards.remove(existing)
            return REMOVED, existing
        return DUPLICATE, existing

    def add_definition(self, term: str, passage: str) -> tuple[str, Flashcard]:
        """A term and the passage the reader marked as its definition."""
        term = " ".join(term.split())
        passage = tidy_selection(passage)
        if not term:
            raise Problem("No term is selected: select the term first.")
        if not passage:
            raise Problem("No definition is marked: drag over the text that defines the term.")
        key = DEFINITION + ":" + term.casefold()
        existing = self._card_with_key(key)
        if existing is not None:
            return DUPLICATE, existing
        return ADDED, self._add(Flashcard(0, DEFINITION, term, passage, key))

    def edit(self, card_id: int, front: str, back: str) -> Flashcard:
        card = self._card(card_id)
        front, back = front.strip(), back.strip()
        if not front or not back:
            raise Problem("A card needs a front and a back; delete the card to remove it.")
        card.front, card.back = front, back
        return card

    def delete(self, card_id: int) -> None:
        self.cards.remove(self._card(card_id))

    def export(self, path: Path) -> None:
        """Write the cards, as the preview shows them, to an .apkg deck."""
        if not self.cards:
            raise Problem("There are no cards yet: pick a word or mark a definition first.")
        write_notes([(card.front_html, card.back_html) for card in self.cards], path)

    def _add(self, card: Flashcard) -> Flashcard:
        card.id = self._next_id
        self._next_id += 1
        self.cards.append(card)
        return card

    def _card(self, card_id: int) -> Flashcard:
        for card in self.cards:
            if card.id == card_id:
                return card
        raise Problem("That card no longer exists.")

    def _card_with_key(self, key: str) -> Flashcard | None:
        for card in self.cards:
            if card.key == key:
                return card
        return None

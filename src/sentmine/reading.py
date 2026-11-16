"""The reading session behind the page: one pasted text and the cards the reader made from it."""

import hashlib
import html
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from sentmine.deck import Note, card_back, card_front, write_notes
from sentmine.history import Entry
from sentmine.lemma import base_form
from sentmine.memory import CardMemory, MemoryProblem
from sentmine.sentences import paragraphs, split_sentences
from sentmine.words import Word, find_words

WORD = "word"
DEFINITION = "definition"

ADDED = "added"
REMOVED = "removed"
DUPLICATE = "duplicate"
EARLIER = "earlier"  # no card made: the memory has one; the reader may make it anyway

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
    earlier: str = ""  # made anyway: the date of the earlier card in the memory
    heading: str = ""  # word cards: the first line of the back; a suggested meaning goes under it
    cloze: bool = False  # definition cards: the passage with the term hidden, instead of term -> passage
    pictures: list[tuple[str, bytes]] = field(default_factory=list)  # parts of a page, on the back: (file name, PNG)
    picture_only: bool = False  # the back shows only the pictures, not the text
    source: str = ""  # the session that made it ("read" or "clip"), so only its own text marks its word
    origin: str = ""  # where it came from, as the deck shows it: a PDF's name, a pasted text, a web page
    text_id: str = ""  # the text it was made from, for the met-again count

    @property
    def history_key(self) -> str:
        """The key without its kind: the base form of the word, or the term in lower case."""
        return self.key.split(":", 1)[1]

    @property
    def can_cloze(self) -> bool:
        """A definition card whose term appears in its passage, so there is something to hide."""
        return self.kind == DEFINITION and _term_pattern(self.front).search(self.back) is not None

    @property
    def front_html(self) -> str:
        if self.kind == WORD:
            return card_front(self.front, self.word).replace("\n", "<br>")
        if self.cloze:
            return _marked_html(self.front, self.back, lambda found: "[...]")
        return _plain_html(self.front)

    @property
    def back_html(self) -> str:
        if self.cloze:
            return _marked_html(self.front, self.back, lambda found: "<b>" + found + "</b>")
        return _plain_html(self.back)

    @property
    def pictures_html(self) -> str:
        return "".join(f'<div><img src="{name}"></div>' for name, _ in self.pictures)

    @property
    def note(self) -> Note:
        """The card as Download and Send to Anki write it; pictures go under the answer."""
        media = tuple(self.pictures)
        if self.cloze:
            return Note((_marked_html(self.front, self.back, lambda found: "{{c1::" + found + "}}"), self.pictures_html),
                        cloze=True, media=media)
        if self.picture_only and self.pictures:
            return Note((self.front_html, self.pictures_html), media=media)
        return Note((self.front_html, self.back_html + self.pictures_html), media=media)


def entry_card(entry: Entry) -> Flashcard:
    """An earlier card from the memory, as a card the page can show."""
    return Flashcard(0, entry.kind, entry.front, entry.back, "", word=entry.word)


def word_back(word: str, base: str) -> str:
    """`skew`, or `sighed (sigh)` when the base form differs from the word."""
    return card_back(word) if base == word else f"{card_back(word)} ({base})"


def _plain_html(text: str) -> str:
    return html.escape(text, quote=False).replace("\n", "<br>")


def _terms_pattern(terms: dict[str, Entry]) -> re.Pattern | None:
    """All remembered terms as one pattern of whole words, ignoring case, longest first; None without terms."""
    if not terms:
        return None
    alternatives = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
    return re.compile(r"(?<!\w)(?:" + alternatives + r")(?!\w)", re.IGNORECASE)


def _term_pattern(term: str) -> re.Pattern:
    """The term as a whole word, ignoring case: "variance" is found in "Variance" but not in "covariance"."""
    return re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)


def _marked_html(term: str, passage: str, mark: Callable[[str], str]) -> str:
    """The passage as HTML, with every place of the term, itself escaped, replaced by `mark(place)`."""
    parts, position = [], 0
    for found in _term_pattern(term).finditer(passage):
        parts.append(_plain_html(passage[position : found.start()]))
        parts.append(mark(_plain_html(found.group())))
        position = found.end()
    parts.append(_plain_html(passage[position:]))
    return "".join(parts)


def tidy(text: str) -> str:
    """Paragraphs separated by one blank line; a line break inside a paragraph becomes a space."""
    return "\n\n".join(_SPACES.sub(" ", paragraph) for paragraph in paragraphs(text))


def tidy_selection(text: str) -> str:
    """A selection from the page: paragraph breaks kept, every other run of spaces made one space."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return _NEWLINES.sub("\n\n", _SPACES.sub(" ", text))


def clickable_words(sentence: str) -> list[Word]:
    """The words of a sentence the reader can pick; a token with a digit is not one."""
    return [word for word in find_words(sentence) if not word.ignored]


CLIP_KINDS = ("word", "definition")


class Deck:
    """The cards being made, one list for the text in Read and the clips from web pages."""

    def __init__(self) -> None:
        self.cards: list[Flashcard] = []
        self.next_id = 1
        self.chosen: int | None = None  # the card pictures from a web page go to; the newest one unless chosen


class Session:
    """One text and its cards, kept in memory for one reader."""

    def __init__(self, memory: CardMemory | None = None, deck: Deck | None = None, name: str = "read") -> None:
        self.paragraphs: list[list[str]] = []  # each paragraph is a list of sentences
        self.deck = deck if deck is not None else Deck()  # shared with the other session when there is one
        self.name = name  # "read" or "clip": which cards are this session's own
        self.origin = "a text"  # what its cards say they came from
        self.memory = memory  # None: the session remembers nothing between runs
        self.text_id = ""  # which text is read: the same words give the same id
        self.clip_kinds: list[str] = []  # for clips from web pages: "word" or "definition", one per paragraph

    @property
    def cards(self) -> list[Flashcard]:
        """Every card of the deck, this session's and the other's."""
        return self.deck.cards

    @property
    def own_cards(self) -> list[Flashcard]:
        return [card for card in self.deck.cards if card.source == self.name]

    @property
    def sentences(self) -> list[str]:
        return [sentence for paragraph in self.paragraphs for sentence in paragraph]

    def load(self, text: str) -> None:
        """Replace the text, and with it the cards made from the old one."""
        tidied = tidy(text)
        if not tidied:
            raise Problem("There is no text to read: paste a text first.")
        self.paragraphs = [split_sentences(paragraph) for paragraph in tidied.split("\n\n")]
        self.deck.cards[:] = [card for card in self.deck.cards if card.source != self.name]   # the old text's cards go
        self.clip_kinds = []
        self.text_id = hashlib.sha256(tidied.encode("utf-8")).hexdigest()[:16]

    def add(self, text: str, kind: str = "word") -> None:
        """A clip from a web page: added after the clips before it, whose cards stay. A definition clip is kept
        as one paragraph, since all of it is the definition."""
        if kind not in CLIP_KINDS:
            raise Problem(f"A clip is a {' or a '.join(CLIP_KINDS)}.")
        tidied = tidy(text)
        if not tidied:
            raise Problem("The selection has no text to read.")
        parts = [" ".join(tidied.split())] if kind == "definition" else tidied.split("\n\n")
        self.paragraphs += [split_sentences(part) for part in parts]
        self.clip_kinds += [kind] * len(parts)
        self.text_id = hashlib.sha256(tidied.encode("utf-8")).hexdigest()[:16]

    def remove_clip(self, number: int) -> None:
        """Take a clip away. Its cards stay, since they hold their own text; the clicked places of the
        clips after it move up, so their words stay marked."""
        if not 0 <= number < len(self.paragraphs):
            raise Problem("That clip is not there any more.")
        first = sum(len(paragraph) for paragraph in self.paragraphs[:number])
        count = len(self.paragraphs[number])
        del self.paragraphs[number]
        if number < len(self.clip_kinds):
            del self.clip_kinds[number]
        for card in self.own_cards:
            if card.place is None:
                continue
            sentence, word = card.place
            if first <= sentence < first + count:
                card.place = None   # its sentence is gone
            elif sentence >= first + count:
                card.place = (sentence - count, word)

    def meet(self, cards: list[tuple[str, str]], day: str | None = None) -> None:
        """Record the remembered cards (kind, key) met in this text. A memory that cannot be written records nothing."""
        if self.memory is None or not self.text_id:
            return
        try:
            self.memory.meet(cards, self.text_id, day or date.today().isoformat())
        except MemoryProblem:
            pass  # reading goes on; only the count on My cards misses this text

    def known_cards(self) -> dict[str, Entry]:
        """The remembered word cards, by base form; empty without a memory."""
        return self.memory.word_cards() if self.memory is not None else {}

    def known_terms(self) -> dict[str, Entry]:
        """The remembered definition cards, by term; empty without a memory."""
        return self.memory.term_cards() if self.memory is not None else {}

    def layout(self, known: dict[str, Entry] | None = None, terms: dict[str, Entry] | None = None) -> list[list[dict]]:
        """The text as the page draws it: paragraphs of sentences, each cut into words and the text between.

        A word that is not picked carries `known` when it has a remembered card: `term:` and the
        term when it is part of a remembered term (`terms`), else its base form when that is
        in `known` (remembered word cards).
        """
        picked = {card.place for card in self.own_cards if card.place is not None}
        known = known or {}
        find_terms = _terms_pattern(terms or {})
        paragraphs = []
        number = 0
        for paragraph in self.paragraphs:
            drawn = []
            for sentence in paragraph:
                pieces = []
                position = 0
                found = [(m.start(), m.end(), " ".join(m.group().lower().split())) for m in find_terms.finditer(sentence)] if find_terms else []
                for index, word in enumerate(clickable_words(sentence)):
                    if word.start > position:
                        pieces.append({"text": sentence[position : word.start]})
                    piece = {
                        "text": sentence[word.start : word.end],
                        "word": index,
                        "picked": (number, index) in picked,
                    }
                    if not piece["picked"]:
                        term = next((key for start, end, key in found if start <= word.start and word.end <= end), None)
                        if term is not None:
                            piece["known"] = "term:" + term  # a term wins over a word card
                        elif known:
                            base = base_form(piece["text"])
                            if base in known:
                                piece["known"] = base
                    pieces.append(piece)
                    position = word.end
                if position < len(sentence):
                    pieces.append({"text": sentence[position:]})
                drawn.append({"sentence": number, "pieces": pieces})
                number += 1
            paragraphs.append(drawn)
        return paragraphs

    def pick_word(self, sentence: int, word: int, anyway: bool = False) -> tuple[str, Flashcard | Entry]:
        """A click on a word: make its card, or remove the card this very word made.

        If the memory already has a card for the word, no card is made and the earlier
        entry comes back, unless `anyway` is true.
        """
        sentences = self.sentences
        if not 0 <= sentence < len(sentences):
            raise Problem("That sentence is not in the text.")
        words = clickable_words(sentences[sentence])
        if not 0 <= word < len(words):
            raise Problem("That word is not in the sentence.")
        text = words[word].text
        base = base_form(text)
        key = WORD + ":" + base
        existing = self._card_with_key(key)
        if existing is None:
            earlier = self._earlier(WORD, base)
            if earlier is not None and not anyway:
                return EARLIER, earlier
            back = word_back(text, base)
            card = Flashcard(
                0, WORD, sentences[sentence], back, key, word=text, place=(sentence, word),
                earlier=earlier.date if earlier else "", heading=back,
            )
            return ADDED, self._add(card)
        if existing.place == (sentence, word) and existing.source == self.name:
            self.cards.remove(existing)
            return REMOVED, existing
        return DUPLICATE, existing

    def add_definition(self, term: str, passage: str, anyway: bool = False) -> tuple[str, Flashcard | Entry]:
        """A term and the passage the reader marked as its definition; the memory is checked as for words."""
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
        earlier = self._earlier(DEFINITION, term.casefold())
        if earlier is not None and not anyway:
            return EARLIER, earlier
        card = Flashcard(0, DEFINITION, term, passage, key, earlier=earlier.date if earlier else "")
        card.cloze = card.can_cloze
        return ADDED, self._add(card)

    def edit(self, card_id: int, front: str, back: str) -> Flashcard:
        card = self._card(card_id)
        front, back = front.strip(), back.strip()
        if not front or not back:
            raise Problem("A card needs a front and a back; delete the card to remove it.")
        card.front, card.back = front, back
        card.cloze = card.cloze and card.can_cloze  # the edit may have taken the term out of the passage
        return card

    def set_cloze(self, card_id: int, cloze: bool) -> Flashcard:
        """Make a definition card a cloze card, or a term -> passage card."""
        card = self._card(card_id)
        if card.kind != DEFINITION:
            raise Problem("Only definition cards can be cloze cards.")
        if cloze and not card.can_cloze:
            raise Problem(f"'{card.front}' is not in the passage, so there is nothing to hide.")
        card.cloze = cloze
        return card

    def delete(self, card_id: int) -> None:
        self.cards.remove(self._card(card_id))

    def add_picture(self, card_id: int, png: bytes) -> Flashcard:
        """Put a picture (a part of a PDF page) on the back of a card; its file name comes from its content."""
        card = self._card(card_id)
        name = "sentmine-" + hashlib.sha256(png).hexdigest()[:16] + ".png"
        if name not in {known for known, _ in card.pictures}:
            card.pictures.append((name, png))
        return card

    def picture(self, card_id: int, number: int) -> bytes:
        """The PNG of a card's picture."""
        pictures = self._card(card_id).pictures
        if not 0 <= number < len(pictures):
            raise Problem("That picture is not on the card any more.")
        return pictures[number][1]

    def remove_picture(self, card_id: int, number: int) -> Flashcard:
        card = self._card(card_id)
        self.picture(card_id, number)   # says so if it is gone
        del card.pictures[number]
        card.picture_only = card.picture_only and bool(card.pictures)
        return card

    def set_picture_only(self, card_id: int, on: bool) -> Flashcard:
        """Show only the pictures on the back of a card, or the text with the pictures under it."""
        card = self._card(card_id)
        if on and not card.pictures:
            raise Problem("Add a picture to the card first.")
        card.picture_only = on
        return card

    def suggest(self, card_id: int, ask: Callable[[str, str], str]) -> Flashcard:
        """Put a meaning from `ask(word, sentence)` on the back, under the word, replacing any earlier one."""
        card = self._card(card_id)
        if card.kind != WORD:
            raise Problem("Only word cards get a suggested meaning: the back of this card is the passage you marked.")
        card.back = f"{card.heading}\n{ask(card.word, card.front)}"
        return card

    def export(self, path: Path, day: str | None = None) -> str:
        """Write the cards, as the preview shows them, to an .apkg deck, then add them to the memory.

        Returns a warning if the deck was written but the cards could not be remembered, else "".
        """
        write_notes(self._notes(), path)
        return self._remember(day, "The deck was made")

    def send(self, deck: str, send_notes: Callable[[list[Note], str], tuple[int, int]],
             day: str | None = None) -> tuple[int, int, str]:
        """Send the cards, as the preview shows them, to Anki, then add them to the memory.

        Returns how many were added, how many were already in the deck, and a warning as export does.
        Nothing is remembered if sending fails.
        """
        added, already = send_notes(self._notes(), deck)
        return added, already, self._remember(day, "The cards are in Anki")

    def _notes(self) -> list[Note]:
        if not self.cards:
            raise Problem("There are no cards yet: pick a word or mark a definition first.")
        return [card.note for card in self.cards]

    def _remember(self, day: str | None, done: str) -> str:
        if self.memory is None:
            return ""
        day = day or date.today().isoformat()
        entries = [
            Entry(card.kind, card.history_key, card.front, card.back, card.word, day) for card in self.cards
        ]
        try:
            self.memory.add(entries)
            # the text each card was made from does not count as meeting it again
            for text_id in {card.text_id for card in self.cards if card.text_id}:
                made = [(card.kind, card.history_key) for card in self.cards if card.text_id == text_id]
                self.memory.made_from(made, text_id, day)
        except MemoryProblem as error:
            return f"{done}, but these cards were not remembered. {error}"
        return ""

    def _add(self, card: Flashcard) -> Flashcard:
        card.id = self.deck.next_id
        self.deck.next_id += 1
        card.source, card.origin, card.text_id = self.name, self.origin, self.text_id
        self.cards.append(card)
        self.deck.chosen = card.id   # a new card is the one its picture is usually for
        return card

    @property
    def chosen_card(self) -> int | None:
        """The card pictures from a web page go to: the one the reader chose, else the newest; None without cards."""
        ids = [card.id for card in self.cards]
        if self.deck.chosen in ids:
            return self.deck.chosen
        return ids[-1] if ids else None

    def choose_card(self, card_id: int) -> Flashcard:
        card = self._card(card_id)
        self.deck.chosen = card.id
        return card

    def _card(self, card_id: int) -> Flashcard:
        for card in self.cards:
            if card.id == card_id:
                return card
        raise Problem("That card no longer exists.")

    def _earlier(self, kind: str, key: str) -> Entry | None:
        return self.memory.find(kind, key) if self.memory is not None else None

    def _card_with_key(self, key: str) -> Flashcard | None:
        for card in self.cards:
            if card.key == key:
                return card
        return None

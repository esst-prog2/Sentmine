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
from sentmine.meaning import key_in
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
    kind: str  # WORD or DEFINITION: how it is found again (a word by its base form); both look the same
    front: str  # the term: a word as written, or the term marked; text and pictures
    back: str  # the passage: the word's sentence, or the marked definition; text and pictures
    key: str  # two cards with the same key are the same card
    word: str = ""  # word cards: the word shown in bold on the front
    place: tuple[int, int] | None = None  # word cards: the sentence and word that were clicked
    earlier: str = ""  # made anyway: the date of the earlier card in the memory
    sentence: str = ""  # word cards: the sentence the word was clicked in, for Suggest meaning
    meaning: str = ""  # word cards: the suggested meaning last put on the back, so a new one replaces it
    key_part: str = ""  # word cards: the words of the sentence that show the suggested meaning, underlined on the back
    old_layout: bool = False  # a word card remembered before 2026-11-18: the sentence on the front, the word on the back
    cloze: bool = False  # the passage with the term hidden, instead of term -> passage
    pictures: list[tuple[str, bytes]] = field(default_factory=list)  # parts of a page, on the back: (file name, PNG)
    source: str = ""  # the session that made it ("read" or "clip"), so only its own text marks its word
    origin: str = ""  # where it came from: a PDF's file name, a web page's title; "" for a pasted text
    origin_url: str = ""  # a web page's address
    origin_place: str = ""  # where in it: "p. 13"
    text_id: str = ""  # the text it was made from, for the met-again count

    @property
    def history_key(self) -> str:
        """The key without its kind: the base form of the word, or the term in lower case."""
        return self.key.split(":", 1)[1]

    @property
    def term(self) -> str:
        """What is marked in the passage, and hidden on a cloze card: the word as written, or the front's text."""
        if self.kind == WORD and self.word and not self.old_layout:
            return self.word
        return without_pictures(self.front)

    @property
    def can_cloze(self) -> bool:
        """The term appears in the passage, so there is something to hide."""
        return not self.old_layout and bool(self.term) and _term_pattern(self.term).search(without_pictures(self.back)) is not None

    @property
    def _front_pictures_html(self) -> str:
        """A cloze card has no front of its own: the front's pictures go after the answer."""
        return "".join(f'<div><img src="{name}"></div>' for name in PICTURE.findall(self.front))

    @property
    def front_html(self) -> str:
        if self.old_layout:
            return _with_pictures(self.front, lambda part: card_front(part, self.word).replace("\n", "<br>"))
        if self.cloze:
            return _marked_html(self.term, self.back, lambda found: "[...]")
        return _plain_html(self.front)

    @property
    def back_html(self) -> str:
        """The passage with the term in bold; a cloze card shows the front's pictures after it."""
        if self.old_layout:
            return _plain_html(self.back)
        bold = _marked_html(self.term, self.back, lambda found: "<b>" + found + "</b>", self.key_part) if self.term else _plain_html(self.back)
        return bold + self._front_pictures_html if self.cloze else bold

    @property
    def origin_text(self) -> str:
        """Where the card came from, as shown: "primer.pdf, p. 13"."""
        return ", ".join(part for part in (self.origin, self.origin_place) if part)

    @property
    def source_html(self) -> str:
        """A small line for the back of the Anki card, so the passage can be found again; none without a real source."""
        if not self.origin or (self.origin == UNNAMED_PAGE and not self.origin_url):
            return ""
        text = html.escape(self.origin_text)
        if self.origin_url:
            text = f'<a href="{html.escape(self.origin_url, quote=True)}">{text}</a>'
        return f'<div style="font-size: 0.8em; color: #777; margin-top: 0.8em">Source: {text}</div>'

    @property
    def note(self) -> Note:
        """The card as Download and Send to Anki write it: the back as the reader arranged it, text and
        pictures, and the source under it."""
        media = tuple(self.pictures)
        if self.cloze:
            return Note((_marked_html(self.term, self.back, lambda found: "{{c1::" + found + "}}", self.key_part),
                         self._front_pictures_html + self.source_html),
                        cloze=True, media=media)
        return Note((self.front_html, self.back_html + self.source_html), media=media)


def entry_card(entry: Entry) -> Flashcard:
    """An earlier card from the memory, as a card the page can show. A word card remembered before both kinds
    looked the same has its sentence on the front and the word (and its meaning) on the back."""
    first_line = entry.back.split("\n", 1)[0]
    old = (entry.kind == WORD and bool(entry.word) and " " in entry.front.strip()
           and re.fullmatch(re.escape(entry.word.lower()) + r"( \(.+\))?", first_line) is not None)
    return Flashcard(0, entry.kind, entry.front, entry.back, "", word=entry.word, old_layout=old)


def word_back(word: str, base: str) -> str:
    """`skew`, or `sighed (sigh)` when the base form differs from the word."""
    return card_back(word) if base == word else f"{card_back(word)} ({base})"


def _plain_html(text: str) -> str:
    return _with_pictures(text, lambda part: html.escape(part, quote=False).replace("\n", "<br>"))


def _terms_pattern(terms: dict[str, Entry]) -> re.Pattern | None:
    """All remembered terms as one pattern of whole words, ignoring case, longest first; None without terms."""
    if not terms:
        return None
    alternatives = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
    return re.compile(r"(?<!\w)(?:" + alternatives + r")(?!\w)", re.IGNORECASE)


def _term_pattern(term: str) -> re.Pattern:
    """The term as a whole word, ignoring case: "variance" is found in "Variance" but not in "covariance"."""
    return re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)


def _marked_html(term: str, passage: str, mark: Callable[[str], str], key: str = "") -> str:
    """The passage as HTML, with every place of the term, itself escaped, replaced by `mark(place)`, and the first
    place of `key` (the words that show a suggested meaning) underlined; its pictures stay where they are."""
    def with_term(text: str) -> str:
        parts, position = [], 0
        for found in _term_pattern(term).finditer(text):
            parts.append(_plain_html(text[position : found.start()]))
            parts.append(mark(_plain_html(found.group())))
            position = found.end()
        parts.append(_plain_html(text[position:]))
        return "".join(parts)

    underlined = [False]

    def marked(text: str) -> str:
        if not key or underlined[0] or key not in text:
            return with_term(text)
        underlined[0] = True
        before, after = text.split(key, 1)
        return with_term(before) + "<u>" + with_term(key) + "</u>" + with_term(after)

    return _with_pictures(passage, marked)


_ANY_SPACE = re.compile(r"\s+")


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    """Where each sentence of `text` (one line, single spaces) begins and ends."""
    spans, cursor = [], 0
    for sentence in split_sentences(text):
        start = text.find(sentence, cursor)
        if start < 0:
            continue
        spans.append((start, start + len(sentence)))
        cursor = start + len(sentence)
    return spans


def whole_sentences(selected: str, before: str = "", after: str = "") -> tuple[str, str]:
    """A selection made loosely, as whole sentences: the sentences it touches, with `before` and `after` the text
    around it on the page. A single word comes back as its sentence and the word, else the word is ""."""
    if not selected.strip():
        return "", ""
    raw = before + selected + after
    first = len(before) + len(selected) - len(selected.lstrip())   # the selection without the spaces around it
    last = len(before) + len(selected.rstrip())
    text = _ANY_SPACE.sub(" ", raw)   # spaces made one; a prefix collapses to a prefix of the same length
    start, end = len(_ANY_SPACE.sub(" ", raw[:first])), len(_ANY_SPACE.sub(" ", raw[:last]))
    middle = text[start:end]
    chosen = [text[a:b] for a, b in _sentence_spans(text) if a < end and b > start]
    passage = " ".join(chosen) if chosen else middle
    word = middle.strip(".,;:!?\"'()[]")
    single = len(clickable_words(word)) == 1 and clickable_words(word)[0].text == word
    return passage, word if single and passage != word else ""


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


# A picture's place in the text of a card's back: [[picture:sentmine-<16 hex>.png]], on a line of its own.
PICTURE = re.compile(r"\n?\[\[picture:(sentmine-[0-9a-f]{16}\.png)\]\]\n?")


def picture_place(name: str) -> str:
    return f"[[picture:{name}]]"


def without_pictures(text: str, instead: str = "") -> str:
    """The text with each picture's place taken out, or replaced by `instead` on a line of its own."""
    return PICTURE.sub(f"\n{instead}\n" if instead else "\n", text).strip()


def _with_pictures(text: str, render: Callable[[str], str]) -> str:
    """The text as HTML: `render` for the text between the pictures, an image where each picture is."""
    parts, position = [], 0
    for found in PICTURE.finditer(text):
        parts.append(render(text[position : found.start()]))
        parts.append(f'<div><img src="{found.group(1)}"></div>')
        position = found.end()
    parts.append(render(text[position:]))
    return "".join(parts)
UNNAMED_PAGE = "a web page"  # a clip whose page gave no title


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
        self.origin = ""  # what its cards say they came from: a file's name; "" for a pasted text
        self.clip_sources: list[tuple[str, str]] = []  # for clips: the page's title and address, one per paragraph
        self.memory = memory  # None: the session remembers nothing between runs
        self.text_id = ""  # which text is read: the same words give the same id

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
        self.clip_sources = []
        self.text_id = hashlib.sha256(tidied.encode("utf-8")).hexdigest()[:16]

    def add(self, text: str, title: str = "", url: str = "") -> None:
        """A clip from a web page (its title and address, when known): one paragraph, added after the clips
        before it, whose cards stay."""
        tidied = " ".join(tidy(text).split())
        if not tidied:
            raise Problem("The selection has no text to read.")
        self.paragraphs.append(split_sentences(tidied))
        self.clip_sources.append((title or UNNAMED_PAGE, url))
        self.text_id = hashlib.sha256(tidied.encode("utf-8")).hexdigest()[:16]

    def add_clip(self, selected: str, before: str = "", after: str = "", term: str = "", title: str = "",
                 url: str = "") -> tuple[str, Flashcard | Entry] | None:
        """A selection from a web page, made whole sentences, as a clip; with a card at once when the selection
        is one word (a card for it, from its sentence) or holds a term in bold (a card for the term, the clip
        as its passage). None when the reader is still to say what the card is for."""
        passage, word = whole_sentences(selected, before, after)
        if not passage:
            raise Problem("The selection has no text to read.")
        self.add(passage, title, url)
        number = len(self.sentences) - len(self.paragraphs[-1])
        if word:
            for index, sentence in enumerate(self.paragraphs[-1]):
                found = [at for at, one in enumerate(clickable_words(sentence)) if one.text == word]
                if found:
                    return self.pick_word(number + index, found[0])
        term = " ".join(term.split())
        if term and len(term) <= 100 and _term_pattern(term).search(" ".join(self.paragraphs[-1])):
            return self.add_definition(term, " ".join(self.paragraphs[-1]))
        return None

    def remove_clip(self, number: int) -> None:
        """Take a clip away. Its cards stay, since they hold their own text; the clicked places of the
        clips after it move up, so their words stay marked."""
        if not 0 <= number < len(self.paragraphs):
            raise Problem("That clip is not there any more.")
        first = sum(len(paragraph) for paragraph in self.paragraphs[:number])
        count = len(self.paragraphs[number])
        del self.paragraphs[number]
        if number < len(self.clip_sources):
            del self.clip_sources[number]
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
            card = Flashcard(
                0, WORD, word_back(text, base), sentences[sentence], key, word=text, place=(sentence, word),
                earlier=earlier.date if earlier else "", sentence=sentences[sentence],
            )
            return ADDED, self._add(card)
        if existing.place == (sentence, word) and existing.source == self.name:
            self.cards.remove(existing)
            return REMOVED, existing
        return DUPLICATE, existing

    def add_definition(self, term: str, passage: str, anyway: bool = False) -> tuple[str, Flashcard | Entry]:
        """A term and the passage the reader marked as its definition; the memory is checked as for words."""
        term = " ".join(term.split())
        passage = self._whole_sentences_of(tidy_selection(passage))
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
        return ADDED, self._add(card)

    def _whole_sentences_of(self, passage: str) -> str:
        """The passage as the whole sentences of the text it touches, paragraph breaks kept; as it is when it is
        not found in the text (as typed)."""
        spans, flat, paragraph_of = [], "", []
        for number, paragraph in enumerate(self.paragraphs):
            for sentence in paragraph:
                if flat:
                    flat += " "
                spans.append((len(flat), len(flat) + len(sentence)))
                paragraph_of.append(number)
                flat += sentence
        wanted = _ANY_SPACE.sub(" ", passage).strip()
        at = flat.find(wanted) if wanted else -1
        if at < 0:
            return passage
        end = at + len(wanted)
        touched = [index for index, (a, b) in enumerate(spans) if a < end and b > at]
        sentences = self.sentences
        parts: list[list[str]] = []
        for index in touched:
            if parts and paragraph_of[index] == paragraph_of[touched[touched.index(index) - 1]]:
                parts[-1].append(sentences[index])
            else:
                parts.append([sentences[index]])
        return "\n\n".join(" ".join(part) for part in parts)

    def edit(self, card_id: int, front: str, back: str) -> Flashcard:
        card = self._card(card_id)
        held = {name for name, _ in card.pictures}
        front, back = (PICTURE.sub(lambda found: found.group() if found.group(1) in held else "\n", side).strip()
                       for side in (front, back))   # only its own pictures, on either side
        if not front or not back:
            raise Problem("A card needs a front and a back; delete the card to remove it.")
        card.front, card.back = front, back
        placed = set(PICTURE.findall(front)) | set(PICTURE.findall(back))
        card.pictures[:] = [(name, png) for name, png in card.pictures if name in placed]   # a picture taken out of the text is gone
        card.cloze = card.cloze and card.can_cloze  # the edit may have taken the term out of the passage
        return card

    def set_cloze(self, card_id: int, cloze: bool) -> Flashcard:
        """Make a card a cloze card, or a term -> passage card."""
        card = self._card(card_id)
        if cloze and not card.can_cloze:
            raise Problem(f"'{card.term}' is not in the passage, so there is nothing to hide.")
        card.cloze = cloze
        return card

    def delete(self, card_id: int) -> None:
        self.cards.remove(self._card(card_id))

    def add_picture(self, card_id: int, png: bytes) -> Flashcard:
        """Put a picture at the end of a card's back, unless it is on the card already; its file name comes
        from its content."""
        card = self._card(card_id)
        name = "sentmine-" + hashlib.sha256(png).hexdigest()[:16] + ".png"
        if name not in {known for known, _ in card.pictures}:
            card.pictures.append((name, png))
        if name not in PICTURE.findall(card.front) + PICTURE.findall(card.back):
            card.back = card.back + "\n" + picture_place(name)   # at the end; the editor can move it
        return card

    def picture(self, card_id: int, name: str) -> bytes:
        """The PNG of a card's picture."""
        for known, png in self._card(card_id).pictures:
            if known == name:
                return png
        raise Problem("That picture is not on the card any more.")

    def suggest(self, card_id: int, ask: Callable[[str, str], str]) -> Flashcard:
        """Put a meaning from `ask(word, sentence)` at the end of the back, replacing the one suggested before."""
        card = self._card(card_id)
        if card.kind != WORD or card.old_layout:
            raise Problem("Only a card made from one word gets a suggested meaning: its passage is your definition.")
        sentence = card.sentence or without_pictures(card.back)
        meaning = ask(card.word, sentence)
        back = card.back
        if card.meaning and ("\n\n" + card.meaning) in back:
            back = back.replace("\n\n" + card.meaning, "", 1)
        card.back, card.meaning = back.rstrip() + "\n\n" + meaning, str(meaning)
        card.key_part = key_in(sentence, getattr(meaning, "key", ""))   # only words that really are in the sentence
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
            Entry(card.kind, card.history_key, without_pictures(card.front, "[picture]"),
                  without_pictures(card.back, "[picture]"), card.word, day,
                  "" if card.origin == UNNAMED_PAGE and not card.origin_url else card.origin,   # no name, no source
                  card.origin_url, card.origin_place) for card in self.cards
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

    def sentence_of(self, card: Flashcard) -> int | None:
        """The sentence of this session's text a card was made from: the clicked one, or the one a marked
        passage starts in; None when it cannot be told."""
        if card.place is not None:
            return card.place[0]
        start = " ".join(card.back.split())[:40]
        for number, sentence in enumerate(self.sentences):
            flat = " ".join(sentence.split())
            if start and (start in flat or flat[:40] in " ".join(card.back.split())):
                return number
        return None

    def _add(self, card: Flashcard) -> Flashcard:
        card.id = self.deck.next_id
        self.deck.next_id += 1
        card.source, card.origin, card.text_id = self.name, self.origin, self.text_id
        sentence = self.sentence_of(card)
        if self.clip_sources and sentence is not None:   # a clip's card comes from that clip's page
            paragraph, seen = 0, 0
            for paragraph, sentences in enumerate(self.paragraphs):
                seen += len(sentences)
                if sentence < seen:
                    break
            if paragraph < len(self.clip_sources):
                card.origin, card.origin_url = self.clip_sources[paragraph]
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

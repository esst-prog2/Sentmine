"""The reading app: a web page served on the reader's own computer."""

import base64
import hashlib
import re
import socket
import tempfile
import threading
import webbrowser
from collections.abc import Callable
from functools import partial
from pathlib import Path
from urllib.parse import quote

from flask import Flask, Response, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge

from sentmine.anki import AnkiProblem, send_notes
from sentmine.deck import Note
from sentmine.document import MOST_BYTES, DocumentProblem, read_file
from sentmine.history import Entry
from sentmine.meaning import MeaningProblem, find_api_key, suggest_meaning
from sentmine.memory import CardMemory, MemoryProblem, RememberedCard, default_memory_path
from sentmine.pages import Pages, locate, part, picture
from sentmine.reading import ADDED, DUPLICATE, EARLIER, REMOVED, Flashcard, Problem, Session, entry_card, picture_name
from sentmine.words import plural

HOST = "127.0.0.1"  # this computer only
FIRST_PORT = 8000
LAST_PORT = 8010
DEFAULT_DECK_NAME = "new"
# The browser is opened a moment after the server starts, so the first page request finds it running.
# 0.8 seconds was chosen by guess, not measured; on a slow computer the page may need a reload.
BROWSER_DELAY_SECONDS = 0.8

_PAGE = Path(__file__).parent / "web" / "index.html"
_CARDS_PAGE = Path(__file__).parent / "web" / "cards.html"
_DATA_MARK = "<!-- first data -->"  # where a page gets the data it first shows
_EXTENSION_ORIGINS = ("chrome-extension://", "extension://", "moz-extension://")  # the browser extension
_NOT_IN_A_FILE_NAME = re.compile(r"[^\w \-]+")


def deck_name(name: str) -> str:
    """The deck name the reader gave, made safe; the same for Download and Send to Anki."""
    return " ".join(_NOT_IN_A_FILE_NAME.sub(" ", name or "").split()) or DEFAULT_DECK_NAME


def deck_file_name(name: str) -> str:
    """A safe file name for the deck the reader named."""
    return deck_name(name) + ".apkg"


PNG_START = b"\x89PNG\r\n\x1a\n"
MOST_PICTURE_BYTES = 5 * 1024 * 1024  # a picture from a web page; a formula or a photo is far smaller


_SRC = re.compile(r'src="(sentmine-[0-9a-f]{16}\.png)"')


def _card_json(card: Flashcard, prefix: str = "") -> dict:
    address = f"{prefix}/api/cards/{card.id}/pictures/"   # a picture's name comes from its content, so it can be cached

    def shown(found: re.Match) -> str:
        return f'src="{address}{found.group(1)}"'

    return {
        "id": card.id,
        "kind": card.kind,
        "front": card.front,
        "back": card.back,
        "front_html": _SRC.sub(shown, card.front_html),
        "back_html": _SRC.sub(shown, card.back_html),
        "earlier": card.earlier,
        "cloze": card.cloze,
        "can_cloze": card.can_cloze,
        # the address carries the picture's name, which comes from its content, so the browser never shows an old one
        "pictures": {name: f"{address}{name}" for name, _ in card.pictures},  # for the editor: where each picture is served
        "source": card.source,  # "read" or "clip"
        "sentences": card.sentences,  # the sentences of its text in its passage, for Add sentences
        "origin": card.origin_text,  # where it came from: "primer.pdf, p. 13", a web page's title
        "origin_url": card.origin_url,
    }


def _png_sent(value) -> bytes:
    """A PNG sent in base64 by the browser extension, checked before it goes on a card."""
    if not isinstance(value, str) or len(value) > MOST_PICTURE_BYTES * 4 // 3 + 4:
        raise Problem("The picture is too large: at most 5 MB.")
    try:
        png = base64.b64decode(value, validate=True)
    except ValueError as error:
        raise Problem("The picture could not be read.") from error
    if not png.startswith(PNG_START):
        raise Problem("Only PNG pictures can be added.")
    return png


def _earlier_json(entry: Entry) -> dict:
    card = entry_card(entry)
    return {"kind": entry.kind, "front_html": card.front_html, "back_html": card.back_html, "date": entry.date}


def _known_json(entry: Entry, met: tuple[int, str] | None) -> dict:
    """A remembered card shown when pointing at its word: as an earlier card, with how often it was met again."""
    return {**_earlier_json(entry), "met_again": _met_again_line(met)}


def _remembered_json(card: RememberedCard, met: tuple[int, str] | None = None) -> dict:
    shown = entry_card(card.entry)
    return {
        "id": card.id,
        "kind": card.entry.kind,
        "front_html": shown.front_html,
        "back_html": shown.back_html,
        "date": card.entry.date,
        "source": ", ".join(part for part in (card.entry.source, card.entry.source_place) if part),
        "source_url": card.entry.source_url,
        "met_again": _met_again_line(met),
    }


def _met_again_line(met: tuple[int, str] | None) -> str:
    """`Met again in 3 texts, last on 2026-11-14`, or "" for a card never met again."""
    if not met:
        return ""
    count, last = met
    return f"Met again in {plural(count, 'text')}, last on {last}"


def _message(result: str, card: Flashcard | Entry) -> str:
    name = card.word or card.front
    if result == EARLIER:
        return f"'{name}' already has a card from {card.date}."
    if result == DUPLICATE:
        return f"'{name}' already has a card."
    if result == REMOVED:
        return f"Removed the card for '{name}'."
    return f"Made a card for '{name}'."


def _known_note(words: int, terms: int = 0) -> str:
    """How many words and terms of a text already have cards, said after reading it."""
    counted = [f"{count} {name}{'' if count == 1 else 's'}" for count, name in ((words, "word"), (terms, "term")) if count]
    if words + terms == 1:
        return f"{counted[0]} you have a card for is underlined."
    return f"{' and '.join(counted)} you have cards for are underlined."


def _sent_message(deck: str, added: int, already: int) -> str:
    if added == 0:
        if already == 1:
            return f"The card was already in the deck '{deck}' in Anki."
        return f"All {plural(already, 'card')} were already in the deck '{deck}' in Anki."
    message = f"Sent to the deck '{deck}' in Anki: {plural(added, 'card')} added"
    if already:
        message += f", {already} {'was' if already == 1 else 'were'} already there"
    return message + ". Now in My cards too."


def create_app(
    session: Session | None = None,
    ask: Callable[[str, str], str] | None = None,
    send: Callable[[list[Note], str], tuple[int, int]] = send_notes,
) -> Flask:
    """`ask(word, sentence)` gives a meaning; without it the page shows no Suggest meaning button.
    `send(notes, deck)` adds notes to Anki; tests give a fake one."""
    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = MOST_BYTES
    read = session if session is not None else Session()
    # Clips from web pages have a text of their own, apart from the text in Read; the cards are one deck.
    clips = Session(read.memory, deck=read.deck, name="clip")
    web_address = re.compile(r"^https?://", re.IGNORECASE)

    def deck_version() -> str:
        """A fingerprint of the deck: Read and the side panel ask for it to see when the other changed a card."""
        seen = hashlib.sha256()
        for card in read.deck.cards:
            seen.update(repr((card.id, card.front, card.back, card.cloze, card.earlier, card.origin_text,
                              [name for name, _ in card.pictures])).encode("utf-8"))
        seen.update(repr(read.chosen_card).encode("utf-8"))
        return seen.hexdigest()[:16]

    def place_in_pdf(result: str, card) -> None:
        """A new card from the PDF in Read says which page it came from."""
        pages = shown["pages"]
        if result != ADDED or now() is not read or pages is None:
            return
        sentence = read.sentence_of(card)
        for number, boxes in enumerate(pages.boxes):
            if any(box[0] == sentence for box in boxes):
                card.origin_place = f"p. {number + 1}"
                return

    def now() -> Session:
        """The session a request is about: under /clip the clips, otherwise the text in Read."""
        return clips if request.path.startswith("/clip") else read

    class _Now:   # `reading` below stands for the session of the request
        def __getattr__(self, name: str):
            return getattr(now(), name)

    reading = _Now()

    def both(method: str, rule: str):
        """A reading route, answered for Read at `rule` and for the clips at /clip + `rule`."""
        def register(view):
            app.add_url_rule(rule, view_func=view, methods=[method])
            app.add_url_rule("/clip" + rule, endpoint="clip_" + view.__name__, view_func=view, methods=[method])
            return view
        return register

    shown: dict = {"pages": None, "version": ""}  # the PDF shown as its own pages, if the text came from one

    def show_pages(pages: Pages | None, data: bytes = b"") -> None:
        shown["pages"] = pages
        # The pictures' address carries a fingerprint of the file, so the browser's cache never gives a picture
        # of another PDF. A counter did not do: it started again at 1 each time sentmine started.
        shown["version"] = hashlib.sha256(data).hexdigest()[:16] if pages is not None else ""

    def pages_of(number: int) -> Pages:
        pages = shown["pages"]
        if pages is None or not 0 <= number < len(pages.sizes):
            raise Problem("That page is not in the PDF being read.")
        return pages

    def state(message: str = "", result: str = "", earlier: Entry | None = None, count_known: bool = False,
              picture: str = ""):
        known, terms = reading.known_cards(), reading.known_terms()
        paragraphs = reading.layout(known, terms)
        in_text = sorted({piece["known"] for p in paragraphs for s in p for piece in s["pieces"] if "known" in piece})
        terms_in_text = [key for key in in_text if key.startswith("term:")]
        if count_known and in_text:
            message = f"{message} {_known_note(len(in_text) - len(terms_in_text), len(terms_in_text))}"
            reading.meet([("definition", key[len("term:"):]) if key.startswith("term:") else ("word", key) for key in in_text])
        met = reading.memory.met_again() if reading.memory is not None and in_text else {}
        return jsonify(
            paragraphs=paragraphs,
            known_cards={
                key: _known_json(*(
                    (terms[key[len("term:"):]], met.get(("definition", key[len("term:"):]))) if key.startswith("term:")
                    else (known[key], met.get(("word", key)))
                )) for key in in_text
            },
            cards=[_card_json(card, "/clip" if now() is clips else "") for card in reading.cards],
            count=len(reading.cards),
            count_text=plural(len(reading.cards), "card"),
            message=message,
            result=result,
            earlier=_earlier_json(earlier) if earlier is not None else None,
            memory_warning=reading.memory.problem if reading.memory is not None else "",
            can_suggest=ask is not None,
            text_id=reading.text_id,  # names the text read, so the page can keep the reader's place in it
            clips=now() is clips,  # the side panel: each paragraph is a clip
            chosen_card=reading.chosen_card,  # where pictures from a web page go
            added_picture=picture,  # the picture just added, so the editor puts it at the cursor even when the card has it
            deck_version=deck_version(),  # changes whenever the deck does, here or in the other view
            pdf=None if shown["pages"] is None or now() is clips else {
                "version": shown["version"],
                "sizes": [[round(width, 2), round(height, 2)] for width, height in shown["pages"].sizes],
                "outline": [{"level": level, "title": title, "page": page} for level, title, page in shown["pages"].outline or []],
            },
        )

    def answer(result: str, card: Flashcard | Entry):
        return state(_message(result, card), result, card if result == EARLIER else None)

    def anyway() -> bool:
        """Optional; when it is sent it must be true or false."""
        value = (request.get_json(silent=True) or {}).get("anyway", False)
        if not isinstance(value, bool):
            raise Problem("The request has no usable 'anyway'.")
        return value

    def sent(name: str, kind: type = str):
        value = (request.get_json(silent=True) or {}).get(name)
        if not isinstance(value, kind) or isinstance(value, bool):
            raise Problem(f"The request has no usable '{name}'.")
        return value

    @app.errorhandler(Problem)
    @app.errorhandler(MemoryProblem)
    @app.errorhandler(MeaningProblem)
    @app.errorhandler(DocumentProblem)
    @app.errorhandler(AnkiProblem)
    def problem(error: Exception):
        return jsonify(error=str(error)), 400

    @app.before_request
    def only_own_pages_change_things():
        """A request that changes something must come from sentmine's own page or a browser extension. A browser
        always names the website a request comes from (Origin), so another site cannot make it post here."""
        origin = request.headers.get("Origin")
        if request.method in ("GET", "HEAD", "OPTIONS") or origin is None:
            return None
        if origin == request.host_url.rstrip("/") or origin.startswith(_EXTENSION_ORIGINS):
            return None
        return jsonify(error="Only sentmine's own page can change what it reads."), 403

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(error: RequestEntityTooLarge):
        return jsonify(error="This file is larger than 50 MB, so it cannot be read."), 413

    def page_with(path: Path, first: Callable[[], Response]) -> Response:
        """The page with the data it first shows inside, so it is drawn complete when it first appears,
        not empty and then filled. Without that data the page asks for it, as before."""
        html = path.read_text(encoding="utf-8")
        try:
            # "<" is written as \u003c: the JSON means the same, and nothing in it can end the script element.
            data = first().get_data(as_text=True).replace("<", "\\u003c")
        except (Problem, MemoryProblem, DocumentProblem):
            return Response(html, mimetype="text/html")
        holder = f'<script type="application/json" id="first-data">{data}</script>'
        return Response(html.replace(_DATA_MARK, holder, 1), mimetype="text/html")

    @app.get("/")
    def page():
        return page_with(_PAGE, state)

    @app.get("/clip")
    def clip_page():
        return page_with(_PAGE, state)

    @app.get("/cards")
    def cards_page():
        return page_with(_CARDS_PAGE, remembered)

    @app.get("/api/memory")
    def remembered():
        memory = reading.memory
        if memory is None:
            return jsonify(cards=[], total=0, total_text=plural(0, "card"), progress=None, memory_warning="This app has no card memory.")
        cards, total = memory.search(request.args.get("q", ""))
        met = memory.met_again()
        return jsonify(
            cards=[_remembered_json(card, met.get((card.entry.kind, card.entry.key))) for card in cards],
            total=total,
            total_text=plural(total, "card"),
            progress=memory.progress(),
            memory_warning=memory.problem,
        )

    @app.delete("/api/memory/<int:card_id>")
    def forget(card_id: int):
        if reading.memory is None:
            raise Problem("This app has no card memory.")
        reading.memory.delete(card_id)
        return remembered()

    @both("GET", "/api/version")
    def version():
        return jsonify(deck=deck_version())

    @app.get("/api/hello")
    def hello():
        """Tells the browser extension that this port is sentmine, not another program."""
        return jsonify(app="sentmine")

    @both("GET", "/api/state")
    def get_state():
        return state()

    @app.post("/api/text")
    def load_text():
        reading.load(sent("text"))
        read.origin = ""
        show_pages(None)
        return state("Text loaded.", count_known=True)

    @app.post("/clip/api/text")
    def add_clip():
        body = request.get_json(silent=True) or {}
        source = body.get("source") if isinstance(body.get("source"), dict) else {}
        title = " ".join(str(source.get("title") or "").split())[:200]
        url = str(source.get("url") or "")[:2000]
        around = {name: body.get(name) if isinstance(body.get(name), str) else "" for name in ("before", "after", "term")}
        made = clips.add_clip(sent("text"), around["before"][-2000:], around["after"][:2000], around["term"][:200],
                              title, url if web_address.match(url) else "")
        if made is None:
            return state("Clip added. Click a word for a card, or drag over the term it explains.", count_known=True)
        return answer(*made)

    @app.delete("/clip/api/clips/<int:number>")
    def remove_clip(number: int):
        clips.remove_clip(number)
        return state("Clip removed. Cards made from it stay.")

    @app.post("/api/file")
    def load_file():
        upload = request.files.get("file")
        if upload is None:
            raise Problem("No file was sent.")
        name, data = upload.filename or "", upload.read()
        text, message = read_file(name, data)
        reading.load(text)
        read.origin = name or "a file"
        show_pages(locate(data, reading.sentences) if name.lower().endswith(".pdf") else None, data)
        return state(message, count_known=True)

    @app.get("/api/pages/<int:number>/words")
    def page_words(number: int):
        pages = pages_of(number)
        response = jsonify(boxes=pages.boxes[number], links=(pages.links or [[]] * len(pages.sizes))[number])
        # Cached only when asked for with this PDF's fingerprint, like the pictures, so another PDF never gets them.
        cached = shown["version"] != "" and request.args.get("v") == shown["version"]
        response.headers["Cache-Control"] = "private, max-age=3600" if cached else "no-store"
        return response

    @app.get("/api/pages/<int:number>.png")
    def page_picture(number: int):
        response = Response(picture(pages_of(number), number), mimetype="image/png")
        response.headers["Cache-Control"] = "private, max-age=3600"  # the address carries the PDF's version
        return response

    @both("POST", "/api/word")
    def pick_word():
        result, card = reading.pick_word(sent("sentence", int), sent("word", int), anyway())
        place_in_pdf(result, card)
        return answer(result, card)

    @both("POST", "/api/definition")
    def add_definition():
        body = request.get_json(silent=True) or {}
        if "sentence" in body:   # a drag over the term: its sentence, or the sentences it ran across
            last = body.get("last", body.get("sentence"))
            if not isinstance(last, int) or isinstance(last, bool):
                raise Problem("The request has no usable 'last'.")
            result, card = reading.add_definition(sent("term"), anyway=anyway(), sentences=(sent("sentence", int), last))
        else:
            result, card = reading.add_definition(sent("term"), sent("passage"), anyway())
        place_in_pdf(result, card)
        return answer(result, card)

    @both("PUT", "/api/cards/<int:card_id>")
    def edit_card(card_id: int):
        reading.edit(card_id, sent("front"), sent("back"))
        return state("Card changed.")

    @both("DELETE", "/api/cards/<int:card_id>")
    def delete_card(card_id: int):
        reading.delete(card_id)
        return state("Card deleted.")

    @both("PUT", "/api/cards/<int:card_id>/sentences")
    def toggle_sentence(card_id: int):
        card, added = reading.toggle_sentence(card_id, sent("sentence", int))
        return state(("Sentence added to" if added else "Sentence taken out of") + f" the card for '{card.word or card.term}'.")

    @both("PUT", "/api/cards/<int:card_id>/cloze")
    def switch_cloze(card_id: int):
        cloze = (request.get_json(silent=True) or {}).get("cloze")
        if not isinstance(cloze, bool):
            raise Problem("The request has no usable 'cloze'.")
        card = reading.set_cloze(card_id, cloze)
        if card.cloze:
            return state(f"Now a cloze card: '{card.term}' is hidden in the passage.")
        return state("Now a term → passage card.")

    @both("POST", "/api/cards/<int:card_id>/meaning")
    def suggest_card_meaning(card_id: int):
        if ask is None:
            raise Problem("Suggesting a meaning needs an API key.")
        reading.suggest(card_id, ask)
        return state("Meaning suggested. Check it, and edit it if you like.")

    @both("POST", "/api/cards/<int:card_id>/pictures")
    def add_picture(card_id: int):
        """A picture for the back of a card: a box drawn on a page of the PDF in Read ({page, box}), or a PNG
        the browser extension took from a web page ({png}, in base64)."""
        body = request.get_json(silent=True) or {}
        if "png" in body:
            png = _png_sent(body["png"])
        else:
            if now() is clips:
                raise Problem("There is no PDF here: add a picture from the web page with a right-click.")
            number = sent("page", int)
            box = body.get("box")
            if not (isinstance(box, list) and len(box) == 4 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in box)):
                raise Problem("The request has no usable 'box'.")
            try:
                png = part(pages_of(number), number, tuple(float(v) for v in box))
            except ValueError as error:
                raise Problem(str(error)) from error
        card = reading.add_picture(card_id, png)
        return state(f"Picture added to the card for '{card.word or card.term}'. Edit the card to move or remove it.",
                     picture=picture_name(png))

    @both("GET", "/api/cards/<int:card_id>/pictures/<name>")
    def card_picture(card_id: int, name: str):
        response = Response(reading.picture(card_id, name), mimetype="image/png")
        response.headers["Cache-Control"] = "private, max-age=3600"  # the address carries the picture's name
        return response

    @both("PUT", "/api/cards/<int:card_id>/chosen")
    def choose_card(card_id: int):
        reading.choose_card(card_id)
        return state("Editing: a picture you paste, or add from a web page, goes on this card.")

    @both("POST", "/api/send")
    def send_to_anki():
        deck = deck_name(sent("deck"))
        added, already, warning = reading.send(deck, send)
        message = _sent_message(deck, added, already)
        return state(message + (" " + warning if warning else ""), "warning" if warning else "sent")

    @both("GET", "/api/deck")
    def download_deck():
        name = deck_file_name(request.args.get("name", ""))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / name
            warning = reading.export(path)
            data = path.read_bytes()
        response = Response(data, mimetype="application/octet-stream")
        response.headers.set("Content-Disposition", "attachment", filename=name)
        if warning:  # the deck is fine, but its cards were not remembered: the page shows why
            response.headers.set("X-Sentmine-Warning", quote(warning))
        return response

    return app


def free_port() -> int:
    """The first port from FIRST_PORT to LAST_PORT that nothing is listening on."""
    for port in range(FIRST_PORT, LAST_PORT + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind((HOST, port))
            except OSError:
                continue
            return port
    raise OSError(f"ports {FIRST_PORT} to {LAST_PORT} are all in use")


def serve(open_browser: bool = True) -> int:
    """Run the reading app until it is stopped with Ctrl+C."""
    port = free_port()
    address = f"http://{HOST}:{port}"
    memory = CardMemory(default_memory_path())
    print(f"sentmine reading app: {address}  (Ctrl+C to stop)")
    if memory.notice:
        print(memory.notice)
    if memory.problem:
        print(f"warning: {memory.problem}")
    else:
        print(f"card memory: {memory.path} ({plural(memory.count(), 'card')})")
    if open_browser:
        threading.Timer(BROWSER_DELAY_SECONDS, webbrowser.open, args=(address,)).start()
    ask = None
    try:
        key = find_api_key()
    except MeaningProblem as error:
        key = ""
        print(f"warning: {error}")
    if key:
        ask = partial(suggest_meaning, key=key)
    print(f"AI meanings: {'on' if ask else 'off (no API key)'}")
    create_app(Session(memory), ask).run(host=HOST, port=port)
    return 0

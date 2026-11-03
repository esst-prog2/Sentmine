"""The reading app: a web page served on the reader's own computer."""

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
from sentmine.document import MOST_BYTES, DocumentProblem, read_file
from sentmine.history import Entry
from sentmine.meaning import MeaningProblem, find_api_key, suggest_meaning
from sentmine.memory import CardMemory, MemoryProblem, RememberedCard, default_memory_path
from sentmine.reading import DUPLICATE, EARLIER, REMOVED, Flashcard, Problem, Session, entry_card
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
_NOT_IN_A_FILE_NAME = re.compile(r"[^\w \-]+")


def deck_name(name: str) -> str:
    """The deck name the reader gave, made safe; the same for Download and Send to Anki."""
    return " ".join(_NOT_IN_A_FILE_NAME.sub(" ", name or "").split()) or DEFAULT_DECK_NAME


def deck_file_name(name: str) -> str:
    """A safe file name for the deck the reader named."""
    return deck_name(name) + ".apkg"


def _card_json(card: Flashcard) -> dict:
    return {
        "id": card.id,
        "kind": card.kind,
        "front": card.front,
        "back": card.back,
        "front_html": card.front_html,
        "back_html": card.back_html,
        "earlier": card.earlier,
    }


def _earlier_json(entry: Entry) -> dict:
    card = entry_card(entry)
    return {"kind": entry.kind, "front_html": card.front_html, "back_html": card.back_html, "date": entry.date}


def _remembered_json(card: RememberedCard) -> dict:
    shown = entry_card(card.entry)
    return {
        "id": card.id,
        "kind": card.entry.kind,
        "front_html": shown.front_html,
        "back_html": shown.back_html,
        "date": card.entry.date,
    }


def _message(result: str, card: Flashcard | Entry) -> str:
    name = card.word or card.front
    if result == EARLIER:
        return f"'{name}' already has a card from {card.date}."
    if result == DUPLICATE:
        return f"'{name}' already has a card."
    if result == REMOVED:
        return f"Removed the card for '{name}'."
    return f"Made a card for '{name}'."


def _sent_message(deck: str, added: int, already: int) -> str:
    if added == 0:
        return f"All {plural(already, 'card')} were already in the deck '{deck}' in Anki."
    message = f"Sent to the deck '{deck}' in Anki: {plural(added, 'card')} added"
    if already:
        message += f", {already} {'was' if already == 1 else 'were'} already there"
    return message + ". Now in My cards too."


def create_app(
    session: Session | None = None,
    ask: Callable[[str, str], str] | None = None,
    send: Callable[[list[tuple[str, str]], str], tuple[int, int]] = send_notes,
) -> Flask:
    """`ask(word, sentence)` gives a meaning; without it the page shows no Suggest meaning button.
    `send(notes, deck)` adds notes to Anki; tests give a fake one."""
    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = MOST_BYTES
    reading = session if session is not None else Session()

    def state(message: str = "", result: str = "", earlier: Entry | None = None):
        return jsonify(
            paragraphs=reading.layout(),
            cards=[_card_json(card) for card in reading.cards],
            count=len(reading.cards),
            count_text=plural(len(reading.cards), "card"),
            message=message,
            result=result,
            earlier=_earlier_json(earlier) if earlier is not None else None,
            memory_warning=reading.memory.problem if reading.memory is not None else "",
            can_suggest=ask is not None,
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

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(error: RequestEntityTooLarge):
        return jsonify(error="This file is larger than 50 MB, so it cannot be read."), 413

    @app.get("/")
    def page():
        return Response(_PAGE.read_text(encoding="utf-8"), mimetype="text/html")

    @app.get("/cards")
    def cards_page():
        return Response(_CARDS_PAGE.read_text(encoding="utf-8"), mimetype="text/html")

    @app.get("/api/memory")
    def remembered():
        memory = reading.memory
        if memory is None:
            return jsonify(cards=[], total=0, total_text=plural(0, "card"), progress=None, memory_warning="This app has no card memory.")
        cards, total = memory.search(request.args.get("q", ""))
        return jsonify(
            cards=[_remembered_json(card) for card in cards],
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

    @app.get("/api/state")
    def get_state():
        return state()

    @app.post("/api/text")
    def load_text():
        reading.load(sent("text"))
        return state("Text loaded.")

    @app.post("/api/file")
    def load_file():
        upload = request.files.get("file")
        if upload is None:
            raise Problem("No file was sent.")
        text, message = read_file(upload.filename or "", upload.read())
        reading.load(text)
        return state(message)

    @app.post("/api/word")
    def pick_word():
        return answer(*reading.pick_word(sent("sentence", int), sent("word", int), anyway()))

    @app.post("/api/definition")
    def add_definition():
        return answer(*reading.add_definition(sent("term"), sent("passage"), anyway()))

    @app.put("/api/cards/<int:card_id>")
    def edit_card(card_id: int):
        reading.edit(card_id, sent("front"), sent("back"))
        return state("Card changed.")

    @app.delete("/api/cards/<int:card_id>")
    def delete_card(card_id: int):
        reading.delete(card_id)
        return state("Card deleted.")

    @app.post("/api/cards/<int:card_id>/meaning")
    def suggest_card_meaning(card_id: int):
        if ask is None:
            raise Problem("Suggesting a meaning needs an API key.")
        reading.suggest(card_id, ask)
        return state("Meaning suggested. Check it, and edit it if you like.")

    @app.post("/api/send")
    def send_to_anki():
        deck = deck_name(sent("deck"))
        added, already, warning = reading.send(deck, send)
        message = _sent_message(deck, added, already)
        return state(message + (" " + warning if warning else ""), "warning" if warning else "sent")

    @app.get("/api/deck")
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

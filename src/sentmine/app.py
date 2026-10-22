"""The reading app: a web page served on the reader's own computer."""

import re
import socket
import tempfile
import threading
import webbrowser
from pathlib import Path
from urllib.parse import quote

from flask import Flask, Response, jsonify, request

from sentmine.history import Entry
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


def deck_file_name(name: str) -> str:
    """A safe file name for the deck the reader named."""
    stem = " ".join(_NOT_IN_A_FILE_NAME.sub(" ", name or "").split())
    return (stem or DEFAULT_DECK_NAME) + ".apkg"


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


def create_app(session: Session | None = None) -> Flask:
    app = Flask(__name__, static_folder=None)
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
    def problem(error: Exception):
        return jsonify(error=str(error)), 400

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
    create_app(Session(memory)).run(host=HOST, port=port)
    return 0

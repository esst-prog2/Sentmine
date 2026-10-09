"""The reading app: a web page served on the reader's own computer."""

import re
import socket
import tempfile
import threading
import webbrowser
from pathlib import Path

from flask import Flask, Response, jsonify, request

from sentmine.reading import ADDED, DUPLICATE, REMOVED, Flashcard, Problem, Session

HOST = "127.0.0.1"  # this computer only
FIRST_PORT = 8000
LAST_PORT = 8010
DEFAULT_DECK_NAME = "new"

_PAGE = Path(__file__).parent / "web" / "index.html"
_NOT_IN_A_FILE_NAME = re.compile(r"[^\w \-]+")


def deck_file_name(name: str) -> str:
    """A safe file name for the deck the reader named."""
    stem = " ".join(_NOT_IN_A_FILE_NAME.sub(" ", name or "").split())
    return (stem or DEFAULT_DECK_NAME) + ".apkg"


def count_text(number: int) -> str:
    return f"{number} card" if number == 1 else f"{number} cards"


def _card_json(card: Flashcard) -> dict:
    return {
        "id": card.id,
        "kind": card.kind,
        "front": card.front,
        "back": card.back,
        "front_html": card.front_html,
        "back_html": card.back_html,
    }


def _message(result: str, card: Flashcard) -> str:
    name = card.word or card.front
    if result == DUPLICATE:
        return f"'{name}' already has a card."
    if result == REMOVED:
        return f"Removed the card for '{name}'."
    return f"Made a card for '{name}'."


def create_app(session: Session | None = None) -> Flask:
    app = Flask(__name__, static_folder=None)
    reading = session if session is not None else Session()

    def state(message: str = "", result: str = ""):
        return jsonify(
            paragraphs=reading.layout(),
            cards=[_card_json(card) for card in reading.cards],
            count=len(reading.cards),
            count_text=count_text(len(reading.cards)),
            message=message,
            result=result,
        )

    def sent(name: str, kind: type = str):
        value = (request.get_json(silent=True) or {}).get(name)
        if not isinstance(value, kind) or isinstance(value, bool):
            raise Problem(f"The request has no usable '{name}'.")
        return value

    @app.errorhandler(Problem)
    def problem(error: Problem):
        return jsonify(error=str(error)), 400

    @app.get("/")
    def page():
        return Response(_PAGE.read_text(encoding="utf-8"), mimetype="text/html")

    @app.get("/api/state")
    def get_state():
        return state()

    @app.post("/api/text")
    def load_text():
        reading.load(sent("text"))
        return state("Text loaded.")

    @app.post("/api/word")
    def pick_word():
        result, card = reading.pick_word(sent("sentence", int), sent("word", int))
        return state(_message(result, card), result)

    @app.post("/api/definition")
    def add_definition():
        result, card = reading.add_definition(sent("term"), sent("passage"))
        return state(_message(result, card), result)

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
            reading.export(path)
            data = path.read_bytes()
        response = Response(data, mimetype="application/octet-stream")
        response.headers.set("Content-Disposition", "attachment", filename=name)
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
    print(f"sentmine reading app: {address}  (Ctrl+C to stop)")
    if open_browser:
        threading.Timer(0.8, webbrowser.open, args=(address,)).start()
    create_app().run(host=HOST, port=port)
    return 0

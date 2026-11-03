"""Add notes to the Anki open on this computer, through the AnkiConnect add-on.

The order of requests is in openspec/specs/send-to-anki and its design: the note type and the
deck are made if missing, cards already in the deck are found first, and only the rest are added.
"""

import json
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence

from sentmine.deck import MODEL

URL = "http://127.0.0.1:8765"  # AnkiConnect's address: this computer only
VERSION = 6
TIMEOUT_SECONDS = 10
ADD_ON_CODE = "2055492159"


class AnkiProblem(Exception):
    """The cards could not be sent; the message says why, in plain words."""


def _not_understood() -> AnkiProblem:
    return AnkiProblem("AnkiConnect gave an answer sentmine does not understand. Update the add-on and try again.")


def _post(body: dict) -> dict:
    """Send one request to AnkiConnect and return its JSON answer."""
    request = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"))
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.load(response)
    except (urllib.error.URLError, ConnectionError, TimeoutError, ValueError):
        raise AnkiProblem(
            "Anki did not answer. Open Anki and try again. If it is open, install the AnkiConnect "
            f"add-on (Tools > Add-ons > Get Add-ons, code {ADD_ON_CODE}) and restart Anki. Download still works."
        ) from None


def _call(post: Callable[[dict], dict], action: str, **params):
    answer = post({"action": action, "version": VERSION, "params": params})
    if not isinstance(answer, dict) or "result" not in answer or "error" not in answer:
        raise _not_understood()
    if answer["error"] is not None:
        if "unsupported action" in str(answer["error"]):
            raise AnkiProblem("This AnkiConnect is too old. Update it in Anki: Tools > Add-ons > Check for Updates.")
        error = answer["error"]
        reasons = sorted(set(map(str, error))) if isinstance(error, list) else [str(error)]
        raise AnkiProblem("Anki refused the cards: " + "; ".join(reasons))
    return answer["result"]


def _make_note_type(post: Callable[[dict], dict]) -> None:
    names = _call(post, "modelNames")
    if not isinstance(names, list):
        raise _not_understood()
    if MODEL.name in names:
        return
    template = MODEL.templates[0]
    _call(
        post,
        "createModel",
        modelName=MODEL.name,
        inOrderFields=[field["name"] for field in MODEL.fields],
        isCloze=False,
        cardTemplates=[{"Name": template["name"], "Front": template["qfmt"], "Back": template["afmt"]}],
    )


def _fronts_in(post: Callable[[dict], dict], deck: str) -> set[str]:
    """The fronts, as HTML, of the sentmine notes already in `deck` (its subdecks left out)."""
    query = f'"deck:{deck}" -"deck:{deck}::*" "note:{MODEL.name}"'
    ids = _call(post, "findNotes", query=query)
    if not isinstance(ids, list):
        raise _not_understood()
    if not ids:
        return set()
    infos = _call(post, "notesInfo", notes=ids)
    try:
        return {info["fields"]["Front"]["value"] for info in infos if info}
    except (TypeError, KeyError):
        raise _not_understood() from None


def send_notes(notes: Sequence[tuple[str, str]], deck: str, post: Callable[[dict], dict] = _post) -> tuple[int, int]:
    """Add (front, back) pairs of HTML to `deck`; returns how many were added and how many were already there.

    A card is already there if a sentmine note in the deck has exactly the same front, bold included. Anki's own
    duplicate check is turned off: it compares fronts without their HTML, so two cards for different words of one
    sentence would look the same to it.
    """
    version = _call(post, "version")
    if not isinstance(version, int) or version < VERSION:
        raise AnkiProblem("This AnkiConnect is too old. Update it in Anki: Tools > Add-ons > Check for Updates.")
    _make_note_type(post)
    _call(post, "createDeck", deck=deck)
    there = _fronts_in(post, deck)
    new = [
        {
            "deckName": deck,
            "modelName": MODEL.name,
            "fields": {"Front": front, "Back": back},
            "options": {"allowDuplicate": True},
        }
        for front, back in notes
        if front not in there
    ]
    if new:
        _call(post, "addNotes", notes=new)
    return len(new), len(notes) - len(new)

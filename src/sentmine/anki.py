"""Add notes to the Anki open on this computer, through the AnkiConnect add-on.

The order of requests is in openspec/specs/send-to-anki and its design: the note type and the
deck are made if missing, cards already in the deck are found first, and only the rest are added.
"""

import json
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence

import genanki

from sentmine.deck import CLOZE_MODEL, MODEL, Note, as_note

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


def _make_note_types(post: Callable[[dict], dict], models: Sequence[genanki.Model]) -> None:
    """Make in Anki each of the sentmine note types that is missing."""
    names = _call(post, "modelNames")
    if not isinstance(names, list):
        raise _not_understood()
    for model in models:
        if model.name in names:
            continue
        template = model.templates[0]
        _call(
            post,
            "createModel",
            modelName=model.name,
            inOrderFields=[field["name"] for field in model.fields],
            isCloze=model.model_type == genanki.Model.CLOZE,
            cardTemplates=[{"Name": template["name"], "Front": template["qfmt"], "Back": template["afmt"]}],
        )


def _first_fields_in(post: Callable[[dict], dict], deck: str) -> set[str]:
    """The first field, as HTML, of each sentmine note of either type already in `deck` (its subdecks left out)."""
    types = " OR ".join(f'"note:{model.name}"' for model in (MODEL, CLOZE_MODEL))
    ids = _call(post, "findNotes", query=f'"deck:{deck}" -"deck:{deck}::*" ({types})')
    if not isinstance(ids, list):
        raise _not_understood()
    if not ids:
        return set()
    infos = _call(post, "notesInfo", notes=ids)
    try:
        return {min(info["fields"].values(), key=lambda field: field["order"])["value"] for info in infos if info}
    except (TypeError, KeyError, AttributeError, ValueError):
        raise _not_understood() from None


def send_notes(notes: Sequence[Note | tuple[str, str]], deck: str, post: Callable[[dict], dict] = _post) -> tuple[int, int]:
    """Add notes, or (front, back) pairs of HTML, to `deck`; returns how many were added and how many were already there.

    A note is already there if a sentmine note in the deck has exactly the same first field, bold included.
    Anki's own duplicate check is turned off: it compares fields without their HTML, so two cards for different
    words of one sentence would look the same to it.
    """
    notes = [as_note(note) for note in notes]
    version = _call(post, "version")
    if not isinstance(version, int) or version < VERSION:
        raise AnkiProblem("This AnkiConnect is too old. Update it in Anki: Tools > Add-ons > Check for Updates.")
    _make_note_types(post, list({note.model.model_id: note.model for note in notes}.values()))
    _call(post, "createDeck", deck=deck)
    there = _first_fields_in(post, deck)
    new = [
        {
            "deckName": deck,
            "modelName": note.model.name,
            "fields": {field["name"]: value for field, value in zip(note.model.fields, note.fields)},
            "options": {"allowDuplicate": True},
        }
        for note in notes
        if note.fields[0] not in there
    ]
    if new:
        _call(post, "addNotes", notes=new)
    return len(new), len(notes) - len(new)

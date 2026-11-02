"""A short explanation of a word in its sentence, from a small OpenAI model.

The model was chosen by the spike in spike/meanings/ (planning log, 2026-11-02):
19 of 20 right, judged blind by the reader, and the cheaper of the two that passed.
"""

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

from sentmine.memory import default_folder

MODEL = "gpt-5-nano"
URL = "https://api.openai.com/v1/chat/completions"
TIMEOUT_SECONDS = 30
KEY_NAME = "OPENAI_API_KEY"
# The same words as in spike/meanings/ask_models.py, so the spike's result applies.
PROMPT = (
    "You explain English words to a learner reading real texts.\n"
    "Word: {word}\nSentence: {sentence}\n"
    "In one short plain English sentence of at most 20 words, explain what the word means "
    "in this sentence. Answer with the explanation only."
)


class MeaningProblem(Exception):
    """No meaning could be had; the message says why, in plain words."""


def find_api_key() -> str:
    """The key from the variable OPENAI_API_KEY, or from .env in the reader's user folder; "" if none."""
    named = os.environ.get(KEY_NAME, "").strip()
    if named:
        return named
    env_file = default_folder() / ".env"
    try:
        lines = env_file.read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError:
        return ""
    except (OSError, UnicodeDecodeError) as error:
        raise MeaningProblem(f"The key file '{env_file}' could not be read ({error}).") from None
    for line in lines:
        if line.startswith(KEY_NAME + "="):
            return line.split("=", 1)[1].strip()
    return ""


def _post(body: dict, key: str) -> dict:
    """Send the request to OpenAI and return its JSON answer."""
    request = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 401:
            raise MeaningProblem("OpenAI refused the API key. Check the key in your .env file.") from None
        if error.code == 429:
            raise MeaningProblem("OpenAI says there is no credit left, or too many requests. Try again later.") from None
        raise MeaningProblem(f"OpenAI answered with an error ({error.code}).") from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise MeaningProblem("OpenAI could not be reached. Check your internet connection.") from None


def suggest_meaning(word: str, sentence: str, key: str, post: Callable[[dict, str], dict] = _post) -> str:
    """A short explanation of `word` as it is used in `sentence`."""
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT.format(word=word, sentence=sentence)}],
        "reasoning_effort": "minimal",
        "max_completion_tokens": 300,
    }
    answer = post(body, key)
    try:
        text = (answer["choices"][0]["message"]["content"] or "").strip()
    except (KeyError, IndexError, TypeError):
        text = ""
    if not text:
        raise MeaningProblem("OpenAI sent back no meaning. Try again.")
    return text

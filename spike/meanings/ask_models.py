"""Spike: ask two small OpenAI models for the meaning of each word, and save everything.

Run from the repository root: python spike/meanings/ask_models.py
Reads OPENAI_API_KEY from .env (never committed). Writes:
  answers.json     every raw answer with its model and token counts (no key in it)
  to_judge.txt     the answers for the reader to mark, model names hidden, order shuffled
  key.json         which answer came from which model: do not open before judging
"""

import json
import random
import urllib.error
import urllib.request
from pathlib import Path

MODELS = ["gpt-5-nano", "gpt-5-mini"]  # both priced on developers.openai.com/api/docs/pricing, 2026-10-17
SEED = 20261102  # fixed, so the shuffle can be repeated
PROMPT = (
    "You explain English words to a learner reading real texts.\n"
    "Word: {word}\nSentence: {sentence}\n"
    "In one short plain English sentence of at most 20 words, explain what the word means "
    "in this sentence. Answer with the explanation only."
)
FOLDER = Path("spike/meanings")


def api_key():
    for line in Path(".env").read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no OPENAI_API_KEY in .env")


def ask(model, word, key):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT.format(**word)}],
        "reasoning_effort": "minimal",
        "max_completion_tokens": 300,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit(f"{model}: HTTP {error.code}: {json.load(error).get('error', {}).get('message')}") from None
    return {
        "model": model,
        "word": word["word"],
        "answer": data["choices"][0]["message"]["content"].strip(),
        "input_tokens": data["usage"]["prompt_tokens"],
        "output_tokens": data["usage"]["completion_tokens"],
    }


key = api_key()
words = json.loads((FOLDER / "words.json").read_text(encoding="utf-8"))
answers = [ask(model, word, key) for word in words for model in MODELS]
(FOLDER / "answers.json").write_text(json.dumps(answers, ensure_ascii=False, indent=1), encoding="utf-8")

shuffle = random.Random(SEED)
lines = [
    "Mark each answer R (right) or W (wrong): does it fit the word in THAT sentence, and would you understand it?",
    "Write the letter at the start of the line, in place of the _.",
    "",
]
hidden = {}
for number, word in enumerate(words, start=1):
    pair = [answer for answer in answers if answer["word"] == word["word"]]
    shuffle.shuffle(pair)
    lines += [f"{number}. {word['word']}", f"   Sentence: {word['sentence']}"]
    for label, answer in zip("ab", pair):
        lines.append(f"_ {number}{label}: {answer['answer']}")
        hidden[f"{number}{label}"] = answer["model"]
    lines.append("")
(FOLDER / "to_judge.txt").write_text("\n".join(lines), encoding="utf-8")
(FOLDER / "key.json").write_text(json.dumps(hidden, indent=1), encoding="utf-8")
print("asked", len(answers), "questions")

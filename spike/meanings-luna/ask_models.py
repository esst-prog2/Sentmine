"""Spike: gpt-5-nano is shut down on 11 December 2026; OpenAI names gpt-6-luna as its replacement. Ask both for the
20 words of spike/meanings/ with the app's own prompt and reading of the answer (sentmine.meaning.suggest_meaning),
and hide which answer is which, so the reader judges them blind, as in the first spike.

Run from the repository root: python spike/meanings-luna/ask_models.py
Uses the same API key as the app (never committed). Writes:
  answers.json     every answer with its model, its key words and token counts (no key in it)
  to_judge.txt     the answers for the reader to mark, model names hidden, order shuffled
  key.json         which answer came from which model: do not open before judging
Count the marks with: python spike/meanings/count_marks.py spike/meanings-luna
"""

import json
import random
from pathlib import Path

from sentmine.meaning import _post, find_api_key, suggest_meaning

# gpt-6-luna refuses reasoning_effort "minimal" (HTTP 400, 2026-11-22); "none" is its lowest
MODELS = {"gpt-5-nano": "minimal", "gpt-6-luna": "none"}
SEED = 20261122  # fixed, so the shuffle can be repeated
FOLDER = Path("spike/meanings-luna")
WORDS = Path("spike/meanings/words.json")


def ask(model, effort, word, key):
    usage = {}

    def post(body, key):
        answer = _post({**body, "model": model, "reasoning_effort": effort}, key)
        usage.update(answer.get("usage") or {})
        return answer

    meaning = suggest_meaning(word["word"], word["sentence"], key, post=post)
    return {"model": model, "word": word["word"], "answer": str(meaning), "key": meaning.key,
            "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens")}


key = find_api_key()
if not key:
    raise SystemExit("no API key: see README")
words = json.loads(WORDS.read_text(encoding="utf-8"))
answers = [ask(model, effort, word, key) for word in words for model, effort in MODELS.items()]
(FOLDER / "answers.json").write_text(json.dumps(answers, ensure_ascii=False, indent=1), encoding="utf-8")

shuffle = random.Random(SEED)
lines = [
    "Mark each answer R (right) or W (wrong): does it fit the word in THAT sentence, and would you understand it?",
    "Write the letter at the start of the line, in place of the _. [the words in brackets would be underlined]",
    "",
]
hidden = {}
for number, word in enumerate(words, start=1):
    pair = [answer for answer in answers if answer["word"] == word["word"]]
    shuffle.shuffle(pair)
    lines += [f"{number}. {word['word']}", f"   Sentence: {word['sentence']}"]
    for label, answer in zip("ab", pair):
        lines.append(f"_ {number}{label}: {answer['answer']}  [{answer['key']}]")
        hidden[f"{number}{label}"] = answer["model"]
    lines.append("")
(FOLDER / "to_judge.txt").write_text("\n".join(lines), encoding="utf-8")
(FOLDER / "key.json").write_text(json.dumps(hidden, indent=1), encoding="utf-8")
print("asked", len(answers), "questions")

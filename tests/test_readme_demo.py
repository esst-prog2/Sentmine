"""readme-demo: what README section 1 shows is what the app makes.

The demo's PDF is copyrighted and not in the repository, so its two sentences are pasted here
as a text; the cards come from the same rules either way. The suggested meaning is the model's
answer on one day and is not checked.
"""

import re
from pathlib import Path

from reading_helper import place_of

from sentmine.app import _message, _sent_message
from sentmine.history import Entry
from sentmine.reading import EARLIER, Session

WORD_SENTENCE = "Two fair coins are flipped simultaneously to determine the payoffs of two players in the town’s casino."
TERM = "Simpson’s reversal"
DEFINITION = (
    "Strangely, the experimental data revealed a Simpson’s reversal: Although the drug proved beneficial to the "
    "population as a whole, drug takers were less likely to recover than nontakers, among both lollipop receivers "
    "and lollipop nonreceivers."
)


def demo() -> str:
    """Section 1 of the README, with every run of spaces and line breaks made one space."""
    text = Path(__file__).parent.parent.joinpath("README.md").read_text(encoding="utf-8")
    section = text[text.index("## 1. The demo") : text.index("## 2.")]
    return " ".join(re.sub(r"\n\s*", " ", section).split())


def flat(text: str) -> str:
    return " ".join(text.split())


def test_the_word_card():
    session = Session()
    session.load(WORD_SENTENCE)
    _, card = session.pick_word(*place_of(session, "simultaneously"))
    shown = demo()
    assert f"front: {flat(card.front)} (simultaneously in bold) back: {card.back}" in shown


def test_the_cloze_card():
    session = Session()
    session.load(DEFINITION)
    _, card = session.add_definition(TERM, DEFINITION)
    assert card.cloze
    assert f"front: {flat(card.front_html)} back: the same sentence, with {TERM} in bold" in demo()


def test_the_messages():
    shown = demo()
    assert f"`{_sent_message('causal', 2, 0)}`" in shown
    earlier = Entry("word", "simultaneously", WORD_SENTENCE, "simultaneously", "simultaneously", "2026-11-07")
    assert f"`{_message(EARLIER, earlier)}`" in shown

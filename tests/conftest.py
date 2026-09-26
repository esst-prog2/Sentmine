"""Shared demo fixtures: the README demo, with the numbers the specs require."""

from types import SimpleNamespace

import pytest

DEMO_PASSAGE = (
    "The stubborn old dog refused to move. Its owner sighed.\n"
    "She was resilient, but the dog was equally stubborn.\n"
)
DEMO_KNOWN = ["dog", "old", "move", "owner"]

DEMO_EXPECTED = SimpleNamespace(
    sentences=3,
    words=19,
    common=8,
    known=5,
    repeats=1,
    cards=5,
    card_words=["stubborn", "refused", "sighed", "resilient", "equally"],
)


@pytest.fixture
def demo_passage() -> str:
    return DEMO_PASSAGE


@pytest.fixture
def demo_known() -> list[str]:
    return list(DEMO_KNOWN)


@pytest.fixture
def demo_expected() -> SimpleNamespace:
    return DEMO_EXPECTED


@pytest.fixture
def demo_files(tmp_path):
    """passage.txt and known.txt on disk, plus the folder that holds them."""
    passage = tmp_path / "passage.txt"
    known = tmp_path / "known.txt"
    passage.write_text(DEMO_PASSAGE, encoding="utf-8")
    known.write_text("\n".join(DEMO_KNOWN) + "\n", encoding="utf-8")
    return SimpleNamespace(folder=tmp_path, passage=passage, known=known)

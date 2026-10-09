"""Homework 5: the link to a real article.

A test would go red if sentmine made a card for a word I did not choose, or if
a card I chose did not show the whole sentence I read.

The expected values below were not produced by running sentmine. The four words
are the ones the reader marked as really new by hand in the Homework 4 spike
(spike/marked_cards_real_irregular.txt). The four sentences were given by the
reader as the sentences of the Guardian article. See PLANNING_LOG.md, 2026-10-09.
"""

from pathlib import Path

import pytest

from sentmine.reading import ADDED, Session

ARTICLE = Path(__file__).parent.parent / "spike" / "article.txt"

# word the reader chose -> the sentence the reader read it in
CHOSEN = {
    "mandate": (
        "Almost a third of voters said an in-out referendum would be needed first, while more than one "
        "in six felt that a general election mandate would be sufficient, and the same proportion "
        "thought parliament could make the decision."
    ),
    "constituencies": (
        "However, there are nerves among some Labour MPs, especially those with constituencies that "
        "voted for Brexit, that even testing out public support for the move would be fraught with "
        "political risk and a potential boost to Reform."
    ),
    "restoke": "But he definitely needs to proceed with caution because we don’t want to restoke division”.",
    "constituents": "My constituents will be cautious.”",
}


def click(session, word):
    """Click the first `word` in the text, as the reader would on the page."""
    for paragraph in session.layout():
        for sentence in paragraph:
            for piece in sentence["pieces"]:
                if "word" in piece and piece["text"].lower() == word:
                    return session.pick_word(sentence["sentence"], piece["word"])
    raise AssertionError(f"{word!r} is not a clickable word of the article")


@pytest.fixture
def reading():
    session = Session()
    session.load(ARTICLE.read_text(encoding="utf-8-sig"))
    for word in CHOSEN:
        result, _ = click(session, word)
        assert result == ADDED
    return session


def test_only_the_words_i_chose_become_cards(reading):
    assert len(reading.cards) == 4
    assert [card.back for card in reading.cards] == list(CHOSEN)


@pytest.mark.parametrize("word", list(CHOSEN))
def test_each_card_shows_the_whole_sentence_i_read(reading, word):
    card = next(card for card in reading.cards if card.back == word)
    assert card.front == CHOSEN[word]

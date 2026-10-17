"""Homework 5: the link to a real article.

A test would go red if sentmine made a card for a word I did not choose, or if
a card I chose did not show the whole sentence I read.

The expected values below were not produced by running sentmine. The four words
are the ones the reader marked as really new by hand in the Homework 4 spike
(spike/marked_cards_real_irregular.txt). See PLANNING_LOG.md, 2026-10-09 and
2026-10-11.

The sentences for `mandate` and `constituencies` were given by the reader on
2026-10-09, after seeing the app's preview of them. The wording for `restoke`
and `constituents`, which lie inside quoted speech, was fixed on 2026-10-11
before the program could produce it: the whole quote with the words that
introduce it, copied from the article text.
"""

from pathlib import Path

import pytest
from reading_helper import place_of

from sentmine.reading import ADDED, Session

ARTICLE = Path(__file__).parent.parent / "spike" / "article.txt"

# word the reader chose -> what the reader read it in
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
    "restoke": (
        "One cabinet minister told the Guardian: “Brexit clearly hasn’t worked and the promises made "
        "haven’t been kept so Andy is right to open up the question of what the future relationship "
        "looks like. But he definitely needs to proceed with caution because we don’t want to restoke "
        "division”."
    ),
    "constituents": (
        "A second said: “Andy is right to say we need some clarity around our long-term relationship. "
        "Security and trade cooperation are higher up the agenda than they were 10 years ago. But "
        "whether that adds up to a real desire for big change in the population I don’t know. My "
        "constituents will be cautious.”"
    ),
}


def click(session, word):
    """Click the first `word` in the text, as the reader would on the page."""
    return session.pick_word(*place_of(session, word))


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

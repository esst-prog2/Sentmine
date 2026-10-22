"""remember-cards: base forms in the session, the earlier card from the history, and adding on download."""

import pytest
from reading_helper import place_of

from sentmine.history import Entry
from sentmine.memory import CardMemory
from sentmine.reading import ADDED, DUPLICATE, EARLIER, Session

SKEW_9_OCT = Entry("word", "skew", "Outliers can skew it considerably.", "skew", "skew", "2026-10-09")
SD_9_OCT = Entry("definition", "standard deviation", "standard deviation", "How spread out values are.", "", "2026-10-09")


@pytest.fixture
def history(tmp_path):
    return CardMemory(tmp_path / "cards.db")


def session_with(history, text):
    reading = Session(history)
    reading.load(text)
    return reading


# --- base forms within one session -------------------------------------------------------


def test_a_word_whose_base_form_differs_shows_it_on_the_back():
    reading = Session()
    reading.load("Its owner sighed.")
    _, card = reading.pick_word(*place_of(reading, "sighed"))
    assert card.back == "sighed (sigh)"
    assert card.back_html == "sighed (sigh)"
    assert card.front_html == "Its owner <b>sighed</b>."


def test_an_irregular_form_of_a_word_makes_no_second_card():
    reading = Session()
    reading.load("They run every day. Yesterday they ran far.")
    reading.pick_word(*place_of(reading, "run"))
    result, _ = reading.pick_word(*place_of(reading, "ran"))
    assert result == DUPLICATE
    assert len(reading.cards) == 1


def test_hoped_and_hopped_are_two_cards():
    reading = Session()
    reading.load("She hoped for rain. The bird hopped away.")
    assert reading.pick_word(*place_of(reading, "hoped"))[0] == ADDED
    assert reading.pick_word(*place_of(reading, "hopped"))[0] == ADDED


def test_a_session_without_a_history_never_answers_earlier():
    reading = Session()
    reading.load("Outliers can skew it considerably.")
    assert reading.pick_word(*place_of(reading, "skew"))[0] == ADDED


# --- the earlier card ---------------------------------------------------------------------


def test_a_word_with_an_earlier_card(history):
    history.add([SKEW_9_OCT])
    reading = session_with(history, "Outliers skewed the results.")
    result, earlier = reading.pick_word(*place_of(reading, "skewed"))
    assert result == EARLIER
    assert earlier == SKEW_9_OCT
    assert reading.cards == []


def test_made_anyway_carries_the_earlier_date(history):
    history.add([SKEW_9_OCT])
    reading = session_with(history, "Outliers skewed the results.")
    result, card = reading.pick_word(*place_of(reading, "skewed"), anyway=True)
    assert result == ADDED
    assert card.earlier == "2026-10-09"
    assert card.back == "skewed (skew)"


def test_a_definition_with_an_earlier_card(history):
    history.add([SD_9_OCT])
    reading = session_with(history, "Some notes.")
    result, earlier = reading.add_definition("Standard  Deviation", "The square root of the variance.")
    assert (result, earlier) == (EARLIER, SD_9_OCT)
    result, card = reading.add_definition("Standard Deviation", "The square root of the variance.", anyway=True)
    assert (result, card.earlier) == (ADDED, "2026-10-09")


def test_a_card_in_this_session_is_a_duplicate_not_an_earlier_card(history):
    history.add([SKEW_9_OCT])
    reading = session_with(history, "Outliers skew it. Polls skew young.")
    reading.pick_word(*place_of(reading, "skew", 0), anyway=True)
    assert reading.pick_word(*place_of(reading, "skew", 1))[0] == DUPLICATE


# --- what the download adds to the history -----------------------------------------------


def test_cards_are_remembered_when_downloaded_not_before(history, tmp_path):
    reading = session_with(history, "Its owner sighed. Outliers can skew it considerably.")
    reading.pick_word(*place_of(reading, "sighed"))
    assert history.entries == []  # made, not yet downloaded
    assert reading.export(tmp_path / "new.apkg", day="2026-10-17") == ""
    assert history.entries == [Entry("word", "sigh", "Its owner sighed.", "sighed (sigh)", "sighed", "2026-10-17")]


def test_a_card_deleted_before_download_is_not_remembered(history, tmp_path):
    reading = session_with(history, "Its owner sighed. Outliers can skew it considerably.")
    _, sighed = reading.pick_word(*place_of(reading, "sighed"))
    reading.pick_word(*place_of(reading, "skew"))
    reading.delete(sighed.id)
    reading.export(tmp_path / "new.apkg", day="2026-10-17")
    assert [entry.key for entry in history.entries] == ["skew"]


def test_the_history_holds_the_edited_text(history, tmp_path):
    reading = session_with(history, "Outliers can skew it considerably.")
    _, card = reading.pick_word(*place_of(reading, "skew"))
    reading.edit(card.id, card.front, "skew: to distort")
    reading.export(tmp_path / "new.apkg", day="2026-10-17")
    assert history.entries[0].back == "skew: to distort"


def test_no_cards_no_deck_and_the_history_is_unchanged(history, tmp_path):
    reading = session_with(history, "Outliers can skew it considerably.")
    with pytest.raises(Exception, match="no cards"):
        reading.export(tmp_path / "new.apkg")
    assert history.entries == []


def test_the_same_deck_downloaded_twice_is_remembered_once(history, tmp_path):
    reading = session_with(history, "Outliers can skew it considerably.")
    reading.pick_word(*place_of(reading, "skew"))
    reading.export(tmp_path / "a.apkg", day="2026-10-17")
    reading.export(tmp_path / "b.apkg", day="2026-10-18")
    assert len(history.entries) == 1


def test_a_definition_card_is_remembered_by_its_term(history, tmp_path):
    reading = session_with(history, "Some notes.")
    reading.add_definition("Standard Deviation", "The square root of the variance.")
    reading.export(tmp_path / "new.apkg", day="2026-10-17")
    assert CardMemory(history.path).find("definition", "standard deviation") is not None


# --- a history that cannot be read --------------------------------------------------------


def test_a_damaged_history_still_lets_the_reader_work_and_download(tmp_path):
    path = tmp_path / "cards.db"
    path.write_text("damaged\n", encoding="utf-8")
    reading = session_with(CardMemory(path), "Outliers can skew it considerably.")
    assert reading.pick_word(*place_of(reading, "skew"))[0] == ADDED
    warning = reading.export(tmp_path / "new.apkg")
    assert "not remembered" in warning and "could not be opened" in warning
    assert (tmp_path / "new.apkg").exists()
    assert path.read_text(encoding="utf-8") == "damaged\n"

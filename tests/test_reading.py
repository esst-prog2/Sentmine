import pytest
from apkg_helper import read_notes

from sentmine.reading import ADDED, DUPLICATE, REMOVED, Problem, Session, tidy

# The paragraph of the README demo, with its line breaks.
NOTES = (
    "The standard deviation measures how spread out a set of values is.\n"
    "It is the square root of the variance. Outliers can skew it\n"
    "considerably.\n"
)
DEFINITION = (
    "The standard deviation measures how spread out a set of values is. "
    "It is the square root of the variance."
)
SKEW_SENTENCE = "Outliers can skew it considerably."


@pytest.fixture
def session():
    reading = Session()
    reading.load(NOTES)
    return reading


def place_of(session, word, nth=0):
    """(sentence, word) numbers of the nth clickable `word` in the text, as the page would send them."""
    places = [
        (sentence["sentence"], piece["word"])
        for paragraph in session.layout()
        for sentence in paragraph
        for piece in sentence["pieces"]
        if "word" in piece and piece["text"].lower() == word
    ]
    return places[nth]


# --- tidying -----------------------------------------------------------------


def test_wrapped_lines_are_joined():
    assert tidy("Outliers can skew it\nconsiderably.") == SKEW_SENTENCE


def test_paragraphs_are_kept_and_extra_blank_lines_dropped():
    assert tidy("One.\n\n\n\n  Two.  \n") == "One.\n\nTwo."


def test_runs_of_spaces_and_tabs_become_one_space():
    assert tidy("a  b\t\tc \r\n d") == "a b c d"


@pytest.mark.parametrize("text", ["", "   ", "\n\n \t\n"])
def test_an_empty_paste_is_refused_and_changes_nothing(session, text):
    session.pick_word(*place_of(session, "skew"))
    with pytest.raises(Problem, match="no text"):
        session.load(text)
    assert len(session.sentences) == 3
    assert len(session.cards) == 1


def test_loading_a_text_discards_the_old_cards(session):
    session.pick_word(*place_of(session, "skew"))
    session.load("Another text.")
    assert session.cards == []
    assert session.sentences == ["Another text."]


# --- the text as the page draws it -------------------------------------------


def test_demo_paragraph_has_three_sentences(session):
    assert session.sentences == [
        "The standard deviation measures how spread out a set of values is.",
        "It is the square root of the variance.",
        SKEW_SENTENCE,
    ]


def test_pieces_put_together_give_the_sentence_back(session):
    for paragraph in session.layout():
        for sentence in paragraph:
            text = "".join(piece["text"] for piece in sentence["pieces"])
            assert text == session.sentences[sentence["sentence"]]


def test_two_paragraphs_are_drawn_as_two():
    reading = Session()
    reading.load("First one. Still first.\n\nSecond.")
    layout = reading.layout()
    assert [len(paragraph) for paragraph in layout] == [2, 1]
    assert [sentence["sentence"] for paragraph in layout for sentence in paragraph] == [0, 1, 2]


def test_a_token_with_a_digit_cannot_be_clicked():
    reading = Session()
    reading.load("It rose 3.5 points in 2026 today.")
    words = [piece["text"] for piece in reading.layout()[0][0]["pieces"] if "word" in piece]
    assert words == ["It", "rose", "points", "in", "today"]


# --- word cards --------------------------------------------------------------


def test_picking_a_word_makes_a_card_from_its_sentence(session):
    result, card = session.pick_word(*place_of(session, "skew"))
    assert result == ADDED
    assert (card.front, card.back) == (SKEW_SENTENCE, "skew")
    assert card.front_html == "Outliers can <b>skew</b> it considerably."
    assert card.back_html == "skew"


def test_the_back_is_lower_cased_and_the_front_keeps_its_capital(session):
    _, card = session.pick_word(*place_of(session, "outliers"))
    assert card.back == "outliers"
    assert card.front_html.startswith("<b>Outliers</b> can")


def test_clicking_the_same_word_again_removes_its_card(session):
    place = place_of(session, "skew")
    session.pick_word(*place)
    result, _ = session.pick_word(*place)
    assert result == REMOVED
    assert session.cards == []


def test_the_picked_word_is_marked_in_the_layout(session):
    place = place_of(session, "skew")
    session.pick_word(*place)
    picked = [
        (sentence["sentence"], piece["word"])
        for paragraph in session.layout()
        for sentence in paragraph
        for piece in sentence["pieces"]
        if piece.get("picked")
    ]
    assert picked == [place]


def test_a_second_occurrence_makes_no_second_card():
    reading = Session()
    reading.load("The stubborn old dog refused to move. She was resilient, but the dog was equally stubborn.")
    reading.pick_word(*place_of(reading, "stubborn", 0))
    result, card = reading.pick_word(*place_of(reading, "stubborn", 1))
    assert result == DUPLICATE
    assert len(reading.cards) == 1
    assert card.front == "The stubborn old dog refused to move."


def test_another_form_of_the_word_makes_no_second_card():
    reading = Session()
    reading.load("Its owner sighed. A sigh is not an answer.")
    reading.pick_word(*place_of(reading, "sighed"))
    result, _ = reading.pick_word(*place_of(reading, "sigh"))
    assert result == DUPLICATE
    assert [card.back for card in reading.cards] == ["sighed"]


@pytest.mark.parametrize("place", [(99, 0), (-1, 0), (0, 99), (0, -1)])
def test_a_place_outside_the_text_is_refused(session, place):
    with pytest.raises(Problem):
        session.pick_word(*place)
    assert session.cards == []


# --- definition cards --------------------------------------------------------


def test_a_two_sentence_definition(session):
    result, card = session.add_definition("standard deviation", DEFINITION)
    assert result == ADDED
    assert (card.front, card.back) == ("standard deviation", DEFINITION)
    assert card.front_html == "standard deviation"  # nothing in bold
    assert card.back_html == DEFINITION


def test_the_definition_is_text_of_the_tidied_page():
    assert DEFINITION in tidy(NOTES)  # the two sentences, joined across the line break


def test_a_definition_across_two_paragraphs_keeps_the_break(session):
    _, card = session.add_definition("variance", "First   paragraph.\n\n\nSecond\tparagraph.")
    assert card.back == "First paragraph.\n\nSecond paragraph."
    assert card.back_html == "First paragraph.<br><br>Second paragraph."


def test_spacing_inside_a_term_is_tidied(session):
    _, card = session.add_definition("  standard \n deviation ", DEFINITION)
    assert card.front == "standard deviation"


def test_the_same_term_again_makes_no_second_card(session):
    session.add_definition("standard deviation", DEFINITION)
    result, _ = session.add_definition("Standard  Deviation", "Something else.")
    assert result == DUPLICATE
    assert [card.back for card in session.cards] == [DEFINITION]


def test_a_word_card_and_a_definition_card_for_the_same_text_can_both_exist(session):
    session.pick_word(*place_of(session, "variance"))
    result, _ = session.add_definition("variance", "The square of the standard deviation.")
    assert result == ADDED
    assert [card.kind for card in session.cards] == ["word", "definition"]


@pytest.mark.parametrize(
    "term, passage, missing",
    [("", DEFINITION, "term"), ("  ", DEFINITION, "term"), ("variance", " \n ", "definition")],
)
def test_an_empty_term_or_passage_is_refused(session, term, passage, missing):
    with pytest.raises(Problem, match=missing):
        session.add_definition(term, passage)
    assert session.cards == []


def test_special_characters_are_escaped_on_both_sides(session):
    _, card = session.add_definition("x < y", "x < y & y > z")
    assert card.front_html == "x &lt; y"
    assert card.back_html == "x &lt; y &amp; y &gt; z"


# --- preview: edit and delete ------------------------------------------------


def test_cards_are_kept_in_the_order_they_were_made(session):
    session.add_definition("standard deviation", DEFINITION)
    session.pick_word(*place_of(session, "skew"))
    assert [card.front for card in session.cards] == ["standard deviation", SKEW_SENTENCE]


def test_editing_changes_the_card(session):
    _, card = session.add_definition("standard deviation", DEFINITION)
    session.edit(card.id, "standard deviation (SD)", "How spread out the values are.")
    assert (card.front, card.back) == ("standard deviation (SD)", "How spread out the values are.")


def test_an_edited_word_card_keeps_its_word_in_bold(session):
    _, card = session.pick_word(*place_of(session, "skew"))
    session.edit(card.id, "Outliers skew it.", "skew: to distort")
    assert card.front_html == "Outliers <b>skew</b> it."
    assert card.back_html == "skew: to distort"


@pytest.mark.parametrize("front, back", [("", "back"), ("front", "  ")])
def test_a_card_cannot_be_edited_to_have_an_empty_side(session, front, back):
    _, card = session.pick_word(*place_of(session, "skew"))
    with pytest.raises(Problem):
        session.edit(card.id, front, back)
    assert (card.front, card.back) == (SKEW_SENTENCE, "skew")


def test_a_deleted_word_can_be_picked_again(session):
    place = place_of(session, "skew")
    _, card = session.pick_word(*place)
    session.delete(card.id)
    assert session.cards == []
    result, _ = session.pick_word(*place)
    assert result == ADDED


def test_a_card_that_does_not_exist_cannot_be_edited_or_deleted(session):
    with pytest.raises(Problem):
        session.edit(7, "a", "b")
    with pytest.raises(Problem):
        session.delete(7)


# --- the deck ----------------------------------------------------------------


def test_the_deck_holds_the_cards_as_the_preview_shows_them(session, tmp_path):
    _, definition = session.add_definition("standard deviation", DEFINITION)
    session.pick_word(*place_of(session, "skew"))
    session.edit(definition.id, "standard deviation", "How spread out a set of values is.")
    deck = tmp_path / "new.apkg"
    session.export(deck)
    notes, _ = read_notes(deck, tmp_path)
    assert [(front, back) for _, front, back in notes] == [
        ("standard deviation", "How spread out a set of values is."),
        ("Outliers can <b>skew</b> it considerably.", "skew"),
    ]


def test_no_cards_no_deck(session, tmp_path):
    deck = tmp_path / "new.apkg"
    with pytest.raises(Problem, match="no cards"):
        session.export(deck)
    assert list(tmp_path.iterdir()) == []

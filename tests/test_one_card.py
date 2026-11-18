"""one-card: every card is the term on the front and the passage on the back; a loose selection is taken as
whole sentences; cards remembered in the earlier layout still show as they were."""

import pytest
from reading_helper import place_of

from sentmine.history import Entry
from sentmine.reading import Session, entry_card, whole_sentences

TEXT = "The median resists outliers. Outliers can skew the mean considerably. A confounder is a variable."


# --- whole sentences ---------------------------------------------------------------------------


@pytest.mark.parametrize("selected, before, after, passage", [
    ("can skew the", "The median resists outliers. Outliers ", " mean considerably. Next.", "Outliers can skew the mean considerably."),
    ("ers. Outliers can", "The median resists outli", " skew the mean. Next.", "The median resists outliers. Outliers can skew the mean."),
    ("Outliers can skew the mean.", "", "", "Outliers can skew the mean."),
    ("  can   skew\n the ", "Outliers\n", "mean.", "Outliers can skew the mean."),   # spaces as a page gives them
])
def test_a_loose_selection_becomes_the_sentences_it_touches(selected, before, after, passage):
    assert whole_sentences(selected, before, after) == (passage, "")


def test_one_word_comes_back_with_its_sentence():
    assert whole_sentences("skew", "Outliers can ", " the mean. Next one.") == ("Outliers can skew the mean.", "skew")


def test_one_word_with_nothing_around_it_is_no_word_card():
    assert whole_sentences("skew") == ("skew", "")


def test_nothing_selected():
    assert whole_sentences("   ") == ("", "")


# --- in Read, a definition drag is snapped to the text's sentences ------------------------------


def test_a_definition_drag_takes_the_whole_sentences_of_the_text():
    session = Session()
    session.load(TEXT)
    _, card = session.add_definition("confounder", "founder is a vari")
    assert card.back == "A confounder is a variable."


def test_a_definition_across_paragraphs_keeps_the_break():
    session = Session()
    session.load("First sentence here. Second one.\n\nThird sentence. Fourth.")
    _, card = session.add_definition("thing", "one.\n\nThird sent")
    assert card.back == "Second one.\n\nThird sentence."


def test_a_passage_that_is_not_in_the_text_is_kept_as_typed():
    session = Session()
    session.load(TEXT)
    _, card = session.add_definition("variance", "How spread out values are.")
    assert card.back == "How spread out values are."


# --- one shape for every card ------------------------------------------------------------------


def test_a_word_card_and_a_definition_card_look_the_same():
    session = Session()
    session.load(TEXT)
    _, word = session.pick_word(*place_of(session, "skew"))
    _, term = session.add_definition("confounder", "A confounder is a variable.")
    assert (word.front_html, word.back_html) == ("skew", "Outliers can <b>skew</b> the mean considerably.")
    assert (term.front_html, term.back_html) == ("confounder", "A <b>confounder</b> is a variable.")
    assert not word.cloze and not term.cloze and word.can_cloze and term.can_cloze


# --- the memory: cards remembered before 2026-11-18 ----------------------------------------------


def test_a_word_card_remembered_in_the_old_layout_shows_as_it_was():
    old = entry_card(Entry("word", "sigh", "Its owner sighed.", "sighed (sigh)\nTo breathe out.", "sighed", "2026-11-01"))
    assert old.old_layout and not old.can_cloze
    assert old.front_html == "Its owner <b>sighed</b>."
    assert old.back_html == "sighed (sigh)<br>To breathe out."


def test_a_word_card_remembered_in_the_new_layout():
    new = entry_card(Entry("word", "sigh", "sighed (sigh)", "Its owner sighed.", "sighed", "2026-11-18"))
    assert not new.old_layout
    assert (new.front_html, new.back_html) == ("sighed (sigh)", "Its owner <b>sighed</b>.")


def test_a_one_word_sentence_is_not_taken_for_the_old_layout():
    new = entry_card(Entry("word", "outlier", "outliers (outlier)", "Outliers can skew it.", "Outliers", "2026-11-18"))
    assert not new.old_layout and new.back_html == "<b>Outliers</b> can skew it."


# --- a few words selected on a web page ----------------------------------------------------------


def test_a_few_words_selected_on_a_web_page_make_their_card_with_the_sentence():
    clips = Session(name="clip")
    made = clips.add_clip("National Tobacco Supply Company", before="The exclusive right of the ",
                          after=", which supplies tobacconists, may be terminated. More text.")
    assert made is not None and made[0] == "added"
    card = made[1]
    assert card.front == "National Tobacco Supply Company"
    assert card.back == "The exclusive right of the National Tobacco Supply Company, which supplies tobacconists, may be terminated."


@pytest.mark.parametrize("selected, before, after", [
    ("one two three four five six seven eight nine", "", " ten."),          # too long for a term
    ("may be terminated. More", "The company ", " text follows."),          # runs over two sentences
    ("The company may be terminated.", "", ""),                             # the whole sentence
])
def test_a_longer_selection_makes_a_card_open_in_edit_for_its_term(selected, before, after):
    clips = Session(name="clip")
    result, card = clips.add_clip(selected, before, after)
    assert result == "added" and card.front == "" and card.key.startswith("passage:")
    assert clips.editing_card() == card.id


def test_the_picture_route_names_the_picture_it_added():
    from sentmine.app import create_app
    import base64
    client = create_app().test_client()
    client.post("/api/text", json={"text": TEXT})
    card = client.post("/api/word", json={"sentence": 1, "word": 2}).get_json()["cards"][0]
    png = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"x" * 20).decode()
    state = client.post(f"/api/cards/{card['id']}/pictures", json={"png": png}).get_json()
    assert state["added_picture"].startswith("sentmine-") and state["added_picture"] in state["cards"][0]["pictures"]
    assert client.get("/api/state").get_json()["added_picture"] == ""

"""Suggest meaning also names the words of the sentence that show the meaning; the card underlines them.
The model is never asked here: its answers are written by hand."""

import pytest
from reading_helper import place_of

from sentmine.meaning import Meaning, key_in, suggest_meaning
from sentmine.reading import Session

SENTENCE = "Two fair coins are flipped simultaneously to determine the payoffs of two players."


def reply(text):
    return {"choices": [{"message": {"content": text}}]}


def asked(text):
    return suggest_meaning("simultaneously", SENTENCE, "k", lambda body, key: reply(text))


def test_the_prompt_asks_for_the_key_on_a_second_line():
    sent = {}
    suggest_meaning("simultaneously", SENTENCE, "k", lambda body, key: sent.update(body=body) or reply("At the same time."))
    assert 'write "Key: "' in sent["body"]["messages"][0]["content"]


def test_the_meaning_and_its_key_are_read_apart():
    meaning = asked("At the same time.\nKey: coins are flipped simultaneously")
    assert meaning == "At the same time." and meaning.key == "coins are flipped simultaneously"


@pytest.mark.parametrize("answer", [
    "At the same time.",                                  # no key line
    "At the same time.\nKey: at the very same moment",    # words not in the sentence
    "At the same time.\nKey: " + SENTENCE,                # the whole sentence is no mark
    "At the same time.\nKey: fair coins are flipped simultaneously to determine the payoffs",   # too long
])
def test_a_key_that_is_not_a_part_of_the_sentence_is_dropped_and_the_meaning_kept(answer):
    meaning = asked(answer)
    assert meaning == "At the same time." and meaning.key == ""


def test_the_key_is_found_ignoring_case_spaces_and_quotes():
    assert key_in(SENTENCE, ' "Flipped   SIMULTANEOUSLY." ') == "flipped simultaneously"
    assert key_in(SENTENCE, "flip") == ""   # a whole word only


# --- on the card ---------------------------------------------------------------------------------


def ask_with_key(key):
    def ask(word, sentence):
        meaning = Meaning("At the same time.")
        meaning.key = key
        return meaning
    return ask


@pytest.fixture
def card():
    session = Session()
    session.load(SENTENCE)
    _, made = session.pick_word(*place_of(session, "simultaneously"))
    session.suggest(made.id, ask_with_key("coins are flipped simultaneously"))
    return session, made


def test_the_key_is_underlined_on_the_back_with_the_word_still_in_bold(card):
    _, made = card
    assert made.back_html.startswith("Two fair <u>coins are flipped <b>simultaneously</b></u> to determine")
    assert made.back_html.endswith("<br><br>At the same time.")
    assert "<u>" not in made.front_html


def test_the_key_goes_to_anki_and_stays_out_of_the_text(card):
    _, made = card
    assert "<u>coins are flipped <b>simultaneously</b></u>" in made.note.fields[1]
    assert "<u>" not in made.back   # the text the reader edits has no markup


def test_an_edit_that_changes_those_words_drops_the_line(card):
    session, made = card
    session.edit(made.id, made.front, made.back.replace("coins are flipped", "coins land"))
    assert "<u>" not in made.back_html


def test_asking_again_replaces_the_key(card):
    session, made = card
    session.suggest(made.id, ask_with_key("not in the sentence at all"))
    assert "<u>" not in made.back_html and made.back.count("At the same time.") == 1


def test_a_cloze_card_keeps_the_line_around_the_gap(card):
    session, made = card
    session.set_cloze(made.id, True)
    assert "<u>coins are flipped {{c1::simultaneously}}</u>" in made.note.fields[0]

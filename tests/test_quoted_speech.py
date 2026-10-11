"""Quoted speech is kept whole: a sentence does not end inside an open quotation."""

from sentmine.sentences import split_sentences


def test_a_quote_of_two_sentences_stays_with_its_introduction():
    text = "One minister said: “It has not worked. But we must be careful”. Nobody replied."
    assert split_sentences(text) == [
        "One minister said: “It has not worked. But we must be careful”.",
        "Nobody replied.",
    ]


def test_the_full_stop_may_come_before_the_closing_mark():
    text = "A second said: “We need clarity. My constituents will be cautious.” The poll agrees."
    assert split_sentences(text) == [
        "A second said: “We need clarity. My constituents will be cautious.”",
        "The poll agrees.",
    ]


def test_straight_quotation_marks_work_the_same_way():
    text = 'She said: "Stop. Go back." Then she left.'
    assert split_sentences(text) == ['She said: "Stop. Go back."', "Then she left."]


def test_guillemets_work_the_same_way():
    text = "Il dit : «Non. Pas encore.» Puis il part."
    assert split_sentences(text) == ["Il dit : «Non. Pas encore.»", "Puis il part."]


def test_a_question_inside_a_quote_does_not_end_it():
    text = "He asked: “Why now? Why us?” Nobody knew."
    assert split_sentences(text) == ["He asked: “Why now? Why us?”", "Nobody knew."]


def test_two_quotes_in_one_paragraph_are_two_sentences():
    text = "“One. Two.” “Three. Four.”"
    assert split_sentences(text) == ["“One. Two.”", "“Three. Four.”"]


def test_sentences_before_and_after_a_quote_split_as_usual():
    text = "It rained. He said: “Stay in. Keep dry.” It rained more. Then it stopped."
    assert split_sentences(text) == [
        "It rained.",
        "He said: “Stay in. Keep dry.”",
        "It rained more.",
        "Then it stopped.",
    ]


def test_a_quote_that_is_never_closed_runs_to_the_end_of_its_paragraph_only():
    text = "He said: “One. Two. Three.\n\nNext paragraph. Second sentence."
    assert split_sentences(text) == [
        "He said: “One. Two. Three.",
        "Next paragraph.",
        "Second sentence.",
    ]


def test_an_apostrophe_is_not_a_quotation_mark():
    text = "We don’t know. They can’t say."
    assert split_sentences(text) == ["We don’t know.", "They can’t say."]

import pytest

from sentmine.sentences import split_sentences


def test_ordinary_sentences():
    assert split_sentences("The dog sat. Its owner sighed.") == ["The dog sat.", "Its owner sighed."]


def test_abbreviation_does_not_end_a_sentence():
    assert split_sentences("Dr. Lee sighed.") == ["Dr. Lee sighed."]


@pytest.mark.parametrize("abbr", ["Mr.", "Mrs.", "Ms.", "Dr.", "St.", "vs.", "etc.", "e.g.", "i.e."])
def test_every_listed_abbreviation(abbr):
    assert len(split_sentences(f"I met {abbr} Smith today.")) == 1


def test_abbreviations_are_case_insensitive():
    assert len(split_sentences("I met DR. Lee and mr. Smith today.")) == 1


def test_decimal_number_does_not_end_a_sentence():
    assert split_sentences("It cost 3.5 million.") == ["It cost 3.5 million."]


def test_closing_quote_followed_by_a_lowercase_word_is_one_sentence():
    assert split_sentences('"Stop!" she said.') == ['"Stop!" she said.']


def test_closing_quote_followed_by_a_capital_letter_is_two_sentences():
    assert split_sentences('"Stop!" She ran.') == ['"Stop!"', "She ran."]


def test_question_mark_followed_by_a_lowercase_word_continues():
    assert split_sentences('"Why?" he asked.') == ['"Why?" he asked.']


def test_curly_closing_quote_stays_with_its_sentence():
    assert split_sentences("“Stop!” She ran.") == ["“Stop!”", "She ran."]


def test_full_stop_followed_by_a_lowercase_word_still_ends_a_sentence():
    assert split_sentences("It ended. and then") == ["It ended.", "and then"]


def test_blank_line_ends_a_sentence():
    text = "A headline without a stop\n\nThe first paragraph starts here."
    assert split_sentences(text) == ["A headline without a stop", "The first paragraph starts here."]


def test_several_blank_lines_and_spaces_on_blank_lines():
    assert split_sentences("One\n  \n\n\nTwo") == ["One", "Two"]


def test_hard_wrapped_sentence_gets_a_single_space():
    assert split_sentences("A sentence that is\nwrapped over two lines.") == [
        "A sentence that is wrapped over two lines."
    ]


def test_windows_line_endings():
    assert split_sentences("One line\r\nof text.\r\n\r\nNext.") == ["One line of text.", "Next."]


def test_text_without_an_end_mark_is_one_sentence():
    assert split_sentences("no end mark here") == ["no end mark here"]


def test_empty_and_blank_text_have_no_sentences():
    assert split_sentences("") == []
    assert split_sentences("  \n\n \n") == []


def test_ellipsis_ends_a_sentence():
    assert split_sentences("Wait... Then she left.") == ["Wait...", "Then she left."]


def test_end_mark_inside_a_word_does_not_split():
    assert split_sentences("Visit example.com now.") == ["Visit example.com now."]


def test_e_g_in_the_middle_of_a_sentence():
    assert split_sentences("Use fruit, e.g. apples, daily.") == ["Use fruit, e.g. apples, daily."]


def test_demo_passage_has_three_sentences(demo_passage, demo_expected):
    sentences = split_sentences(demo_passage)
    assert len(sentences) == demo_expected.sentences
    assert sentences[0] == "The stubborn old dog refused to move."
    assert sentences[1] == "Its owner sighed."
    assert sentences[2] == "She was resilient, but the dog was equally stubborn."

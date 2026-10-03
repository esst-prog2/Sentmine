import pytest

from sentmine.analyse import load_stopwords


def test_list_has_228_words():
    assert len(load_stopwords()) == 228


@pytest.mark.parametrize("word", ["the", "to", "its", "she", "was", "but"])
def test_demo_common_words_are_in_the_list(word):
    assert word in load_stopwords()


@pytest.mark.parametrize("word", ["equally", "refused", "old", "dog", "move", "owner"])
def test_demo_content_words_are_not_in_the_list(word):
    assert word not in load_stopwords()


def test_attribution_comment_is_not_a_stopword():
    words = load_stopwords()
    assert not any(w.startswith("#") for w in words)


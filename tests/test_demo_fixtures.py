def test_demo_numbers_add_up(demo_expected):
    e = demo_expected
    assert e.words == e.common + e.known + e.repeats + e.cards
    assert len(e.card_words) == e.cards


def test_demo_fixtures_are_available(demo_passage, demo_known, demo_files):
    assert demo_passage.startswith("The stubborn old dog")
    assert demo_known == ["dog", "old", "move", "owner"]
    assert demo_files.passage.read_text(encoding="utf-8") == demo_passage
    assert demo_files.known.read_text(encoding="utf-8").split() == demo_known

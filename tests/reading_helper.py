"""Find a clickable word on the page, as the reader would click it."""


def place_of(text, word, nth=0):
    """(sentence, word) numbers of the nth clickable `word`.

    `text` is a Session or the paragraphs it draws (`Session.layout()`, or the
    `paragraphs` of the app's state), which have the same shape.
    """
    paragraphs = text.layout() if hasattr(text, "layout") else text
    places = [
        (sentence["sentence"], piece["word"])
        for paragraph in paragraphs
        for sentence in paragraph
        for piece in sentence["pieces"]
        if "word" in piece and piece["text"].lower() == word
    ]
    if len(places) <= nth:
        raise AssertionError(f"{word!r} is not a clickable word of the text")
    return places[nth]

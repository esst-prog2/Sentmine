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


class _Answer:
    def __init__(self, data):
        self.data, self.status_code = data, 200

    def get_json(self):
        return self.data


def post_clip(client, body):
    """A clip from a web page, as a right-click sends it, for the tests that make their cards from its words: the
    card the right-click makes (the selection as its term) is deleted, as the reader might."""
    before = {card["id"] for card in client.get("/clip/api/state").get_json()["cards"]}
    response = client.post("/clip/api/text", json=body)
    if response.status_code != 200:
        return response
    made = [card["id"] for card in response.get_json()["cards"] if card["id"] not in before]
    for card in made:
        client.delete(f"/clip/api/cards/{card}")
    return _Answer(client.get("/clip/api/state").get_json())

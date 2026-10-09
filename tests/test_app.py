import pytest
from apkg_helper import read_notes
from test_reading import DEFINITION, NOTES

from sentmine.app import HOST, count_text, create_app, deck_file_name


@pytest.fixture
def client():
    return create_app().test_client()


def word_place(state, word):
    for paragraph in state["paragraphs"]:
        for sentence in paragraph:
            for piece in sentence["pieces"]:
                if piece.get("word") is not None and piece["text"].lower() == word:
                    return {"sentence": sentence["sentence"], "word": piece["word"]}
    raise AssertionError(f"{word!r} is not a clickable word")


def test_the_page_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b"<title>sentmine</title>" in response.data


def test_a_new_app_has_no_text_and_no_cards(client):
    state = client.get("/api/state").get_json()
    assert (state["paragraphs"], state["cards"], state["count_text"]) == ([], [], "0 cards")


@pytest.mark.parametrize("number, text", [(0, "0 cards"), (1, "1 card"), (2, "2 cards")])
def test_singular_and_plural_agree_with_the_number(number, text):
    assert count_text(number) == text


def test_the_readme_demo_from_paste_to_deck(client, tmp_path):
    state = client.post("/api/text", json={"text": NOTES}).get_json()
    assert sum(len(paragraph) for paragraph in state["paragraphs"]) == 3

    state = client.post("/api/definition", json={"term": "standard deviation", "passage": DEFINITION}).get_json()
    assert (state["result"], state["count_text"]) == ("added", "1 card")

    skew = word_place(state, "skew")
    state = client.post("/api/word", json=skew).get_json()
    assert (state["result"], state["count_text"]) == ("added", "2 cards")
    assert state["cards"][1]["front_html"] == "Outliers can <b>skew</b> it considerably."

    state = client.post("/api/word", json=skew).get_json()  # clicked again by mistake
    assert (state["result"], state["count_text"]) == ("removed", "1 card")
    state = client.post("/api/word", json=skew).get_json()
    assert state["count_text"] == "2 cards"

    definition = state["cards"][0]
    shorter = "How spread out a set of values is; the square root of the variance."
    state = client.put(
        f"/api/cards/{definition['id']}", json={"front": definition["front"], "back": shorter}
    ).get_json()
    assert state["cards"][0]["back"] == shorter

    response = client.get("/api/deck?name=new")
    assert response.status_code == 200
    assert "new.apkg" in response.headers["Content-Disposition"]
    deck = tmp_path / "new.apkg"
    deck.write_bytes(response.data)
    notes, _ = read_notes(deck, tmp_path)
    assert [(front, back) for _, front, back in notes] == [
        ("standard deviation", shorter),
        ("Outliers can <b>skew</b> it considerably.", "skew"),
    ]


def test_a_duplicate_says_so_and_changes_nothing(client):
    client.post("/api/text", json={"text": "The stubborn dog. An equally stubborn owner."})
    client.post("/api/word", json={"sentence": 0, "word": 1})
    state = client.post("/api/word", json={"sentence": 1, "word": 2}).get_json()
    assert state["result"] == "duplicate"
    assert state["count"] == 1
    assert "already has a card" in state["message"]


def test_deleting_a_card(client):
    client.post("/api/text", json={"text": NOTES})
    state = client.post("/api/definition", json={"term": "variance", "passage": "Something."}).get_json()
    state = client.delete(f"/api/cards/{state['cards'][0]['id']}").get_json()
    assert (state["cards"], state["count_text"]) == ([], "0 cards")


def test_download_with_no_cards_gives_no_file(client):
    client.post("/api/text", json={"text": NOTES})
    response = client.get("/api/deck?name=new")
    assert response.status_code == 400
    assert "no cards" in response.get_json()["error"]


@pytest.mark.parametrize(
    "method, url, body",
    [
        ("post", "/api/text", {"text": "   "}),
        ("post", "/api/text", {}),
        ("post", "/api/text", {"text": 5}),
        ("post", "/api/word", {"sentence": 0, "word": 0}),  # no text loaded
        ("post", "/api/word", {"sentence": "0", "word": 0}),
        ("post", "/api/word", {"sentence": True, "word": 0}),
        ("post", "/api/definition", {"term": "", "passage": "x"}),
        ("post", "/api/definition", {"term": "x"}),
        ("put", "/api/cards/1", {"front": "a", "back": "b"}),  # no such card
        ("delete", "/api/cards/1", None),
    ],
)
def test_a_problem_comes_back_as_400_with_a_message(client, method, url, body):
    response = getattr(client, method)(url, json=body)
    assert response.status_code == 400
    assert response.get_json()["error"]


def test_an_empty_paste_leaves_the_text_and_cards(client):
    client.post("/api/text", json={"text": NOTES})
    client.post("/api/definition", json={"term": "variance", "passage": "Something."})
    assert client.post("/api/text", json={"text": ""}).status_code == 400
    state = client.get("/api/state").get_json()
    assert state["count"] == 1
    assert state["paragraphs"][0][2]["pieces"][0]["text"] == "Outliers"


@pytest.mark.parametrize(
    "name, file_name",
    [
        ("new", "new.apkg"),
        ("", "new.apkg"),
        ("  Statistics week 5 ", "Statistics week 5.apkg"),
        ("../../evil", "evil.apkg"),
        ('a"b/c', "a b c.apkg"),
    ],
)
def test_the_deck_file_name_is_safe(name, file_name):
    assert deck_file_name(name) == file_name


def test_the_app_listens_on_this_computer_only():
    assert HOST == "127.0.0.1"

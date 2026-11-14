"""open-in-sentmine: the app answers who it is, and only its own page or an extension can change it."""

import io

import pytest
from pdf_helper import make_pdf

from sentmine.app import create_app


@pytest.fixture
def client():
    return create_app().test_client()


OWN = "http://localhost"   # the test client's own address


def reading(client):
    return [piece["text"] for p in client.get("/api/state").get_json()["paragraphs"] for s in p for piece in s["pieces"]]


def test_hello_names_the_app(client):
    assert client.get("/api/hello").get_json() == {"app": "sentmine"}


@pytest.mark.parametrize("origin", [None, OWN, "chrome-extension://abcdefghijklmnop", "moz-extension://1234"])
def test_its_own_page_an_extension_and_the_command_line_can_send_text(client, origin):
    headers = {"Origin": origin} if origin else {}
    response = client.post("/api/text", json={"text": "Outliers can skew it."}, headers=headers)
    assert response.status_code == 200
    assert "skew" in reading(client)


@pytest.mark.parametrize("origin", ["https://evil.example", "http://127.0.0.1:9999", "null"])
def test_another_website_cannot_send_a_file(client, origin):
    client.post("/api/text", json={"text": "The first text stays."})
    data = make_pdf([["A text from somewhere else."]])
    response = client.post("/api/file", data={"file": (io.BytesIO(data), "x.pdf")},
                           content_type="multipart/form-data", headers={"Origin": origin})
    assert response.status_code == 403
    assert "first" in reading(client) and "somewhere" not in reading(client)


def test_reading_requests_are_never_refused(client):
    # GET is never refused: the browser's own rules keep other sites from reading the answer.
    assert client.get("/", headers={"Origin": "https://evil.example"}).status_code == 200

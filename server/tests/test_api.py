"""End-to-end API tests. Background tasks run right after each response in TestClient."""

from app.core.errors import UpstreamError
from app.services import ingest_service
from app.services.url_fetcher import FetchedPage

DENTIST_NOTE = "Dentist appointment is on 24 Nov at 4:30 pm at Apollo Clinic."


def add_note(client, content: str = DENTIST_NOTE) -> dict:
    response = client.post("/ingest", json={"type": "note", "content": content})
    assert response.status_code == 202
    return response.json()


def get_items(client) -> list[dict]:
    response = client.get("/items")
    assert response.status_code == 200
    return response.json()["items"]


# ---------- /ingest + /items ----------


def test_note_is_accepted_then_becomes_ready(client):
    created = add_note(client)
    assert created["status"] == "pending"

    [item] = get_items(client)
    assert item["id"] == created["id"]
    assert item["status"] == "ready"
    assert item["chunk_count"] == 1
    assert item["title"] == DENTIST_NOTE
    assert item["created_at"].endswith("+00:00")  # timezone kept


def test_blank_note_is_rejected(client):
    response = client.post("/ingest", json={"type": "note", "content": "   "})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["field"] == "note.content"


def test_invalid_url_and_unknown_type_are_rejected(client):
    assert client.post("/ingest", json={"type": "url", "url": "hello"}).status_code == 422
    assert client.post("/ingest", json={"type": "pdf", "content": "x"}).status_code == 422


def test_url_is_fetched_and_indexed(client, monkeypatch):
    page = FetchedPage(title="Example article", text="Interview tips. " * 100)
    monkeypatch.setattr(ingest_service, "fetch_page", lambda url: page)

    client.post("/ingest", json={"type": "url", "url": "https://example.com/a"})

    [item] = get_items(client)
    assert item["status"] == "ready"
    assert item["title"] == "Example article"
    assert item["chunk_count"] > 1


def test_unreachable_url_fails_with_reason(client, monkeypatch):
    def unreachable(url: str) -> FetchedPage:
        raise UpstreamError("Could not reach this URL.")

    monkeypatch.setattr(ingest_service, "fetch_page", unreachable)
    client.post("/ingest", json={"type": "url", "url": "https://nope.invalid"})

    [item] = get_items(client)
    assert item["status"] == "failed"
    assert item["error"] == "Could not reach this URL."
    assert item["chunk_count"] == 0


def test_embedding_outage_marks_item_failed(client, fake_ai):
    fake_ai.fail_embeddings = True
    add_note(client)

    [item] = get_items(client)
    assert item["status"] == "failed"
    assert "embedding service" in item["error"]


# ---------- /query ----------


def test_question_is_answered_with_cited_source(client):
    add_note(client)
    add_note(client, "Interview tips: explain tradeoffs and commit often.")

    response = client.post("/query", json={"question": "When is my dentist visit?"})

    assert response.status_code == 200
    body = response.json()
    assert "[1]" in body["answer"]
    [source] = body["sources"]
    assert source["index"] == 1
    assert source["snippet"] == DENTIST_NOTE  # the dentist note, not the interview one


def test_unrelated_question_skips_the_llm(client, fake_ai):
    add_note(client)

    response = client.post("/query", json={"question": "What is my bank balance?"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "I couldn't find anything about that in your saved items.",
        "sources": [],
    }
    assert fake_ai.completion_calls == 0


def test_too_short_question_is_rejected(client):
    response = client.post("/query", json={"question": "hi"})
    assert response.status_code == 422


# ---------- errors ----------


def test_unknown_route_uses_error_shape(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"

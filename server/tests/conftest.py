"""Shared test setup: a throwaway database and a fake AI provider (no network, no cost)."""

import os
import tempfile

# Must run before the app is imported: settings and the DB engine read these at import time.
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["OPENAI_API_KEY"] = "sk-test-not-used"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.models import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import create_app  # noqa: E402
from app.providers.openai_provider import get_ai_provider  # noqa: E402

TOPICS = ("dentist", "interview")


class FakeAI:
    """Deterministic stand-in for OpenAI.

    Each text becomes a tiny "topic" vector: texts about the same topic point the
    same way, so similarity search behaves predictably in tests.
    """

    def __init__(self) -> None:
        self.answer = "Your dentist appointment is on 24 Nov [1]."
        self.completion_calls = 0
        self.fail_embeddings = False

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.fail_embeddings:
            from app.core.errors import UpstreamError

            raise UpstreamError("The embedding service is unavailable. Please try again.")
        return [self._vector(text) for text in texts]

    def complete(self, system: str, user: str) -> str:
        self.completion_calls += 1
        return self.answer

    @staticmethod
    def _vector(text: str) -> list[float]:
        lowered = text.lower()
        topic = [1.0 if word in lowered else 0.0 for word in TOPICS]
        other = [0.0 if any(topic) else 1.0]
        return topic + other + [0.0] * 1533


@pytest.fixture
def fake_ai() -> FakeAI:
    return FakeAI()


@pytest.fixture
def client(fake_ai: FakeAI):
    Base.metadata.drop_all(bind=engine)  # every test starts with an empty database
    app = create_app()
    app.dependency_overrides[get_ai_provider] = lambda: fake_ai
    with TestClient(app) as test_client:  # "with" runs the lifespan (creates tables)
        yield test_client

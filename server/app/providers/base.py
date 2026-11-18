"""Interfaces for AI services, so the rest of the app doesn't depend on OpenAI directly."""

from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text, in the same order."""
        ...


class LLMProvider(Protocol):
    def complete(self, system: str, user: str) -> str:
        """Return the model's reply to a system + user prompt."""
        ...


class AIProvider(EmbeddingProvider, LLMProvider, Protocol):
    """Something that can both embed text and answer prompts."""

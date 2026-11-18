"""OpenAI implementation of the embedding and LLM interfaces."""

from functools import lru_cache

import structlog
from openai import OpenAI, OpenAIError

from app.core.config import Settings, get_settings
from app.core.errors import UpstreamError

logger = structlog.get_logger("openai")

EMBED_BATCH_SIZE = 100  # texts per API call


class OpenAIProvider:
    def __init__(self, settings: Settings) -> None:
        self._client = OpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
            timeout=30.0,
            max_retries=2,  # the SDK retries rate limits and network blips for us
        )
        self._embedding_model = settings.embedding_model
        self._chat_model = settings.chat_model

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[start : start + EMBED_BATCH_SIZE]
            try:
                response = self._client.embeddings.create(model=self._embedding_model, input=batch)
            except OpenAIError as exc:
                logger.error("embedding_failed", error=str(exc), batch_size=len(batch))
                raise UpstreamError("The embedding service is unavailable. Please try again.") from exc
            ordered = sorted(response.data, key=lambda item: item.index)
            vectors.extend(item.embedding for item in ordered)
        logger.info("embedded", count=len(texts), model=self._embedding_model)
        return vectors

    def complete(self, system: str, user: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._chat_model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except OpenAIError as exc:
            logger.error("completion_failed", error=str(exc))
            raise UpstreamError("The answer service is unavailable. Please try again.") from exc
        usage = response.usage
        logger.info(
            "completed",
            model=self._chat_model,
            prompt_tokens=usage.prompt_tokens if usage else None,
            completion_tokens=usage.completion_tokens if usage else None,
        )
        return response.choices[0].message.content or ""


@lru_cache
def get_ai_provider() -> OpenAIProvider:
    """FastAPI dependency: one shared client for the whole app."""
    return OpenAIProvider(get_settings())
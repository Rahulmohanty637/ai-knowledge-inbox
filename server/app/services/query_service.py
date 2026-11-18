"""RAG: embed the question -> retrieve chunks -> ask the LLM -> return answer + cited sources."""

import re

import structlog
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.providers.base import AIProvider
from app.schemas.query import QueryResponse, SourceOut
from app.services.prompt_builder import SYSTEM_PROMPT, build_user_prompt
from app.services.retriever import RetrievedChunk, retrieve

logger = structlog.get_logger("query")

NOT_FOUND_ANSWER = "I couldn't find anything about that in your saved items."
SNIPPET_LENGTH = 300
_CITATION = re.compile(r"\[(\d+)\]")


def answer_question(db: Session, question: str, top_k: int | None, ai: AIProvider) -> QueryResponse:
    settings = get_settings()
    [query_vector] = ai.embed([question])
    retrieved = retrieve(db, query_vector, top_k=top_k or settings.top_k, min_score=settings.min_score)
    logger.info(
        "chunks_retrieved",
        count=len(retrieved),
        top_score=round(retrieved[0].score, 3) if retrieved else None,
    )

    if not retrieved:  # nothing relevant: skip the LLM call entirely
        return QueryResponse(answer=NOT_FOUND_ANSWER, sources=[])

    answer = ai.complete(SYSTEM_PROMPT, build_user_prompt(question, retrieved)).strip()
    cited = cited_numbers(answer, max_number=len(retrieved))
    if cited:
        sources = [_to_source(n, retrieved[n - 1]) for n in cited]
    elif answer.lower().startswith("i couldn't find"):
        sources = []
    else:  # the model answered without citing: show everything it was given
        sources = [_to_source(n, hit) for n, hit in enumerate(retrieved, start=1)]
    return QueryResponse(answer=answer, sources=sources)


def cited_numbers(answer: str, max_number: int) -> list[int]:
    """The distinct [n] numbers in the answer, in order of first use, ignoring out-of-range ones."""
    numbers: list[int] = []
    for match in _CITATION.findall(answer):
        n = int(match)
        if 1 <= n <= max_number and n not in numbers:
            numbers.append(n)
    return numbers


def _to_source(number: int, hit: RetrievedChunk) -> SourceOut:
    text = hit.chunk.text
    snippet = text if len(text) <= SNIPPET_LENGTH else text[: SNIPPET_LENGTH - 1] + "…"
    return SourceOut(
        index=number,
        item_id=hit.item.id,
        chunk_id=hit.chunk.id,
        source_type=hit.item.source_type,
        title=hit.item.title,
        url=hit.item.url,
        snippet=snippet,
        score=round(hit.score, 3),
    )
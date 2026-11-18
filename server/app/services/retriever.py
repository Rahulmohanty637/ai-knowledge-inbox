"""Semantic search: find the stored chunks most similar to a query vector."""

from dataclasses import dataclass

import numpy as np
from sqlalchemy.orm import Session

from app.db.models import Chunk, Item
from app.repositories import chunk_repo
from app.services.vectors import from_bytes


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    item: Item
    score: float


def cosine_scores(matrix: np.ndarray, query: np.ndarray) -> np.ndarray:
    """Cosine similarity of `query` against every row of `matrix` (one row per chunk)."""
    norms = np.linalg.norm(matrix, axis=1) * np.linalg.norm(query)
    norms[norms == 0] = 1e-12  # avoid dividing by zero
    return (matrix @ query) / norms


def top_indices(scores: np.ndarray, top_k: int, min_score: float) -> list[int]:
    """Indices of the best `top_k` scores, highest first, ignoring any below `min_score`."""
    best_first = np.argsort(scores)[::-1][:top_k]
    return [int(i) for i in best_first if scores[i] >= min_score]


def retrieve(db: Session, query_vector: list[float], *, top_k: int, min_score: float) -> list[RetrievedChunk]:
    rows = chunk_repo.list_ready_chunks(db)
    if not rows:
        return []
    matrix = np.vstack([from_bytes(chunk.embedding) for chunk, _ in rows])
    scores = cosine_scores(matrix, np.asarray(query_vector, dtype=np.float32))
    return [
        RetrievedChunk(chunk=rows[i][0], item=rows[i][1], score=float(scores[i]))
        for i in top_indices(scores, top_k, min_score)
    ]
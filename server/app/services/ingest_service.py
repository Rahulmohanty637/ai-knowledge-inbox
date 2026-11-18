"""Ingestion pipeline: Extract -> Transform (chunk + embed) -> Load."""

import structlog
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError, BadInputError
from app.db.models import Item
from app.db.session import SessionLocal
from app.providers.base import EmbeddingProvider
from app.repositories import chunk_repo, item_repo
from app.schemas.items import NoteIngest, UrlIngest
from app.services.chunker import chunk_text
from app.services.url_fetcher import fetch_page
from app.services.vectors import to_bytes

logger = structlog.get_logger("ingest")

TITLE_LENGTH = 80


def create_item(db: Session, request: NoteIngest | UrlIngest) -> Item:
    """Save the item as 'pending' and return it straight away."""
    if isinstance(request, NoteIngest):
        item = item_repo.create_item(db, source_type="note", raw_content=request.content)
    else:
        item = item_repo.create_item(db, source_type="url", url=str(request.url))
    db.commit()
    logger.info("item_created", item_id=item.id, source_type=item.source_type)
    return item


def process_item(item_id: str, embedder: EmbeddingProvider) -> None:
    """Background job. Opens its own DB session: the request's session is closed by now."""
    settings = get_settings()
    with SessionLocal() as db:
        item = item_repo.get_item(db, item_id)
        if item is None:
            logger.warning("item_missing", item_id=item_id)
            return

        try:
            title, text = _extract(item)  # Extract
            chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)  # Transform
            if not chunks:
                raise BadInputError("There is no text to index in this item.")
            vectors = embedder.embed(chunks)
            chunk_repo.add_chunks(db, item.id, chunks, [to_bytes(v) for v in vectors])  # Load
            item_repo.mark_ready(db, item, title=title, raw_content=text)
            db.commit()
            logger.info("item_ready", item_id=item.id, chunks=len(chunks))
        except AppError as exc:
            _fail(db, item, exc.message)
        except Exception:
            logger.exception("item_processing_crashed", item_id=item_id)
            _fail(db, item, "Something went wrong while processing this item.")


def _extract(item: Item) -> tuple[str | None, str]:
    """Return (title, text) for the item: the note itself, or the downloaded page."""
    if item.source_type == "url":
        page = fetch_page(item.url or "")
        return page.title or item.url, page.text
    text = item.raw_content or ""
    first_line = text.strip().splitlines()[0] if text.strip() else ""
    return first_line[:TITLE_LENGTH], text


def _fail(db: Session, item: Item, message: str) -> None:
    db.rollback()  # discard any half-written chunks
    item_repo.mark_failed(db, item, message)
    db.commit()
    logger.warning("item_failed", item_id=item.id, error=message)

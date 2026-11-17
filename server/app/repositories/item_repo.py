from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Item


def create_item(
    db: Session,
    *,
    source_type: str,
    url: str | None = None,
    raw_content: str | None = None,
) -> Item:
    item = Item(source_type=source_type, url=url, raw_content=raw_content, status="pending")
    db.add(item)
    db.flush()  # sends the INSERT so item.id is available, without committing
    return item


def get_item(db: Session, item_id: str) -> Item | None:
    return db.get(Item, item_id)


def list_items_with_chunk_counts(db: Session) -> list[tuple[Item, int]]:
    """All items, newest first, each paired with how many chunks it has."""
    stmt = (
        select(Item, func.count(Chunk.id))
        .outerjoin(Chunk, Chunk.item_id == Item.id)
        .group_by(Item.id)
        .order_by(Item.created_at.desc())
    )
    return [(item, count) for item, count in db.execute(stmt).all()]


def mark_ready(db: Session, item: Item, *, title: str | None, raw_content: str) -> None:
    item.title = title
    item.raw_content = raw_content
    item.status = "ready"
    item.error = None


def mark_failed(db: Session, item: Item, error: str) -> None:
    item.status = "failed"
    item.error = error
"""Read-side helpers: turn stored items into API responses."""

from sqlalchemy.orm import Session

from app.db.models import Item
from app.repositories import item_repo
from app.schemas.items import ItemOut

PREVIEW_LENGTH = 200


def _preview(text: str | None) -> str:
    if not text:
        return ""
    text = " ".join(text.split())
    return text if len(text) <= PREVIEW_LENGTH else text[: PREVIEW_LENGTH - 1] + "…"


def to_item_out(item: Item, chunk_count: int) -> ItemOut:
    return ItemOut(
        id=item.id,
        source_type=item.source_type,
        title=item.title,
        url=item.url,
        preview=_preview(item.raw_content),
        status=item.status,
        error=item.error,
        chunk_count=chunk_count,
        created_at=item.created_at,
    )


def list_items(db: Session) -> list[ItemOut]:
    return [to_item_out(item, count) for item, count in item_repo.list_items_with_chunk_counts(db)]
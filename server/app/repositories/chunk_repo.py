from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Item


def add_chunks(db: Session, item_id: str, texts: list[str], embeddings: list[bytes]) -> None:
    db.add_all(
        Chunk(item_id=item_id, chunk_index=i, text=text, embedding=embedding)
        for i, (text, embedding) in enumerate(zip(texts, embeddings, strict=True))
    )


def list_ready_chunks(db: Session) -> list[tuple[Chunk, Item]]:
    """Every chunk belonging to a 'ready' item, with its item (used for search)."""
    stmt = select(Chunk, Item).join(Item, Chunk.item_id == Item.id).where(Item.status == "ready")
    return [(chunk, item) for chunk, item in db.execute(stmt).all()]

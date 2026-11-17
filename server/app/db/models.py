import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Item(Base):
    """One thing the user saved: a note or a URL."""

    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    source_type: Mapped[str] = mapped_column(String(10))           # "note" | "url"
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="pending", index=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )


class Chunk(Base):
    """A piece of an item's text plus its embedding vector."""

    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    item_id: Mapped[str] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[bytes] = mapped_column(LargeBinary)  # float32 array as bytes

    item: Mapped[Item] = relationship(back_populates="chunks")
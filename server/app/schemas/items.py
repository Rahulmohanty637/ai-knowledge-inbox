from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_serializer

SourceType = Literal["note", "url"]
ItemStatus = Literal["pending", "ready", "failed"]


# ---------- Requests ----------


class NoteIngest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    type: Literal["note"]
    content: str = Field(min_length=1, max_length=20_000)


class UrlIngest(BaseModel):
    type: Literal["url"]
    url: HttpUrl


# Pydantic looks at "type" to decide which model to validate against.
IngestRequest = Annotated[NoteIngest | UrlIngest, Field(discriminator="type")]


# ---------- Responses ----------


class ItemOut(BaseModel):
    id: str
    source_type: SourceType
    title: str | None
    url: str | None
    preview: str
    status: ItemStatus
    error: str | None
    chunk_count: int
    created_at: datetime

    @field_serializer("created_at")
    def _as_utc(self, value: datetime) -> str:
        """SQLite drops timezone info; we always store UTC, so re-attach it."""
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat()


class ItemListOut(BaseModel):
    items: list[ItemOut]

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.items import SourceType


class QueryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=3, max_length=1000)
    top_k: int | None = Field(default=None, ge=1, le=10)


class SourceOut(BaseModel):
    index: int  # the [n] number used in the answer
    item_id: str
    chunk_id: str
    source_type: SourceType
    title: str | None
    url: str | None
    snippet: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceOut]
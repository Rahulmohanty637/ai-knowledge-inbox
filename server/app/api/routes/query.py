from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.providers.base import AIProvider
from app.providers.openai_provider import get_ai_provider
from app.schemas.query import QueryRequest, QueryResponse
from app.services import query_service

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(
    body: QueryRequest,
    db: Session = Depends(get_db),
    ai: AIProvider = Depends(get_ai_provider),
) -> QueryResponse:
    """Answer a question from saved items, with cited sources."""
    return query_service.answer_question(db, body.question, body.top_k, ai)

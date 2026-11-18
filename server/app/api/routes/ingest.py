from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.providers.base import EmbeddingProvider
from app.providers.openai_provider import get_ai_provider
from app.schemas.items import IngestRequest, ItemOut
from app.services import ingest_service, item_service

router = APIRouter(tags=["ingest"])


@router.post("/ingest", status_code=202, response_model=ItemOut)
def ingest(
    body: IngestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    embedder: EmbeddingProvider = Depends(get_ai_provider),
) -> ItemOut:
    """Save a note or URL and process it in the background."""
    item = ingest_service.create_item(db, body)
    background_tasks.add_task(ingest_service.process_item, item.id, embedder)
    return item_service.to_item_out(item, chunk_count=0)

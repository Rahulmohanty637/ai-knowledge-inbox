from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.items import ItemListOut
from app.services import item_service

router = APIRouter(tags=["items"])


@router.get("/items", response_model=ItemListOut)
def list_items(db: Session = Depends(get_db)) -> ItemListOut:
    """All saved items, newest first, with processing status."""
    return ItemListOut(items=item_service.list_items(db))

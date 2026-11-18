from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ingest, items, query
from app.core.config import get_settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.db.models import Base
from app.db.session import SessionLocal, engine
from app.middleware.request_context import RequestContextMiddleware
from app.repositories import item_repo


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Runs once at startup (before yield) and once at shutdown (after yield)."""
    logger = structlog.get_logger("app")
    Base.metadata.create_all(bind=engine)  # creates tables if they don't exist
    logger.info("database_ready", tables=list(Base.metadata.tables))

    # Background jobs live in memory, so a restart loses any that were running.
    with SessionLocal() as db:
        interrupted = item_repo.fail_pending_items(
            db, "Processing was interrupted by a server restart. Please add it again."
        )
        db.commit()
    if interrupted:
        logger.warning("interrupted_items_failed", count=interrupted)
    yield


def create_app() -> FastAPI:
    settings = get_settings()  # fails fast if config is missing or invalid
    configure_logging(settings.log_level)

    app = FastAPI(
        title="AI Knowledge Inbox",
        description="Save notes and URLs, then ask questions over them.",
        version="0.1.0",
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    app.include_router(ingest.router)
    app.include_router(items.router)
    app.include_router(query.router)  

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    structlog.get_logger("app").info("app_created", chat_model=settings.chat_model)
    return app


app = create_app()
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware
from app.core.error_handlers import register_exception_handlers

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.db.models import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)  # creates tables if they don't exist
    structlog.get_logger("app").info(
        "database_ready", tables=list(Base.metadata.tables)
    )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
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

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    structlog.get_logger("app").info("app_created", chat_model=settings.chat_model)
    return app


app = create_app()

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware
from app.core.error_handlers import register_exception_handlers


def create_app() -> FastAPI:
    settings = get_settings() 
    configure_logging(settings.log_level)
    
    app = FastAPI(
        title="AI Knowledge Inbox",
        description="Save notes and URLs, then ask questions over them.",
        version="0.1.0",
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

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Knowledge Inbox",
        description="Save notes and URLs, then ask questions over them.",
        version="0.1.0",
    )
    
    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}
    
    return app

app = create_app()

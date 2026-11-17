from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import AppError

logger = structlog.get_logger("errors")

HTTP_CODES = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}


def _error_response(status_code: int, code: str, message: str, details: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
    )


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    log = logger.error if exc.status_code >= 500 else logger.warning
    log("app_error", code=exc.code, message=exc.message, path=request.url.path)
    return _error_response(exc.status_code, exc.code, exc.message, exc.details)


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in err["loc"][1:]),  # skip "body"/"query"
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    logger.warning("validation_error", path=request.url.path, details=details)
    return _error_response(422, "VALIDATION_ERROR", "Request validation failed", details)


async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = HTTP_CODES.get(exc.status_code, "HTTP_ERROR")
    return _error_response(exc.status_code, code, str(exc.detail))


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    # The request middleware already logged the full traceback.
    # Never send internal details to the client.
    return _error_response(500, "INTERNAL_ERROR", "Something went wrong. Please try again.")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
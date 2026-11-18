from typing import Any


class AppError(Exception):
    """Base class for errors we expect and want to show to the client."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class BadInputError(AppError):
    """Input is well-formed but can't be used (e.g. a URL with no readable text)."""

    status_code = 400
    code = "BAD_INPUT"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class UpstreamError(AppError):
    """A service we depend on (OpenAI, a website) failed."""

    status_code = 502
    code = "UPSTREAM_ERROR"

"""Download a web page and extract its readable text."""

import re
from dataclasses import dataclass

import httpx
import structlog
import trafilatura

from app.core.errors import BadInputError, UpstreamError

logger = structlog.get_logger("url_fetcher")

TIMEOUT_SECONDS = 10.0
MAX_BYTES = 2_000_000  # 2 MB
ALLOWED_CONTENT_TYPES = {"text/html", "application/xhtml+xml", "text/plain"}
USER_AGENT = (
    "AIKnowledgeInbox/0.1 (+https://github.com/Rahulmohanty637/ai-knowledge-inbox)"
)
_FOOTNOTE_MARKER = re.compile(r"\[(\d+|citation needed|note \d+)\]")


@dataclass(frozen=True)
class FetchedPage:
    title: str | None
    text: str


def fetch_page(url: str) -> FetchedPage:
    """Download `url` and return its title and main text, or raise a clear AppError."""
    raw, content_type = _download(url)
    if content_type == "text/plain":
        return FetchedPage(title=None, text=raw)
    return _extract_article(raw, url)


def _download(url: str) -> tuple[str, str]:
    try:
        with httpx.Client(
            timeout=TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9",
            },
        ) as client, client.stream("GET", url) as response:
            if response.status_code >= 400:
                raise BadInputError(_http_error_message(response.status_code))

            content_type = (
                response.headers.get("content-type", "").split(";")[0].strip().lower()
            )
            if content_type not in ALLOWED_CONTENT_TYPES:
                raise BadInputError(
                    f"Unsupported content type '{content_type or 'unknown'}'. "
                    "Only web pages and plain text are supported."
                )

            body = bytearray()
            for part in response.iter_bytes():
                body.extend(part)
                if len(body) > MAX_BYTES:
                    raise BadInputError("The page is too large (over 2 MB).")
            encoding = response.encoding or "utf-8"
    except httpx.TimeoutException as exc:
        raise UpstreamError("The website took too long to respond.") from exc
    except httpx.RequestError as exc:
        raise UpstreamError("Could not reach this URL.") from exc

    logger.info("page_downloaded", url=url, bytes=len(body), content_type=content_type)
    return body.decode(encoding, errors="replace"), content_type


def _http_error_message(status: int) -> str:
    if status in (401, 403):
        return f"The website refused access (HTTP {status}). Some sites block automated readers."
    if status == 404:
        return "Page not found (HTTP 404). Check the URL."
    if status >= 500:
        return f"The website had an error (HTTP {status}). Try again later."
    return f"The page returned HTTP {status}."


def _extract_article(html: str, url: str) -> FetchedPage:
    text = trafilatura.extract(
        html, url=url, include_comments=False, include_tables=True
    )
    if not text:
        raise BadInputError("Could not find readable text on this page.")
    text = _FOOTNOTE_MARKER.sub("", text)  # drop "[1]"-style refs; we use [n] for our own citations
    metadata = trafilatura.extract_metadata(html, default_url=url)
    title = metadata.title if metadata and metadata.title else None
    return FetchedPage(title=title, text=text)

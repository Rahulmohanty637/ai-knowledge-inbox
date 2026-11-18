"""Split text into overlapping chunks that respect paragraph and sentence boundaries."""

import re

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def normalize_text(text: str) -> str:
    """Unify line endings, collapse runs of spaces and blank lines, trim the ends."""
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _split_into_units(text: str, size: int) -> list[str]:
    """Break text into pieces no longer than `size`: paragraphs, else sentences, else hard cuts."""
    units: list[str] = []
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= size:
            units.append(paragraph)
            continue
        for sentence in _SENTENCE_BOUNDARY.split(paragraph):
            sentence = sentence.strip()
            while len(sentence) > size:  # a single huge "sentence": cut it
                units.append(sentence[:size])
                sentence = sentence[size:].strip()
            if sentence:
                units.append(sentence)
    return units


def _overlap_tail(chunk: str, overlap: int) -> str:
    """The last ~`overlap` characters of a chunk, starting at a word boundary."""
    if overlap == 0 or len(chunk) <= overlap:
        return ""
    tail = chunk[-overlap:]
    first_space = tail.find(" ")
    return tail[first_space + 1 :] if first_space != -1 else tail


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Pack paragraphs/sentences into chunks of at most `size` characters.

    Each new chunk starts with the last ~`overlap` characters of the previous one,
    so an idea that straddles a boundary still appears whole in at least one chunk.
    """
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Need size > 0 and 0 <= overlap < size")

    text = normalize_text(text)
    if not text:
        return []

    chunks: list[str] = []
    current = ""
    for unit in _split_into_units(text, size):
        candidate = f"{current} {unit}" if current else unit
        if len(candidate) <= size:
            current = candidate
            continue
        chunks.append(current)
        tail = _overlap_tail(current, overlap)
        current = (
            f"{tail} {unit}" if tail and len(tail) + 1 + len(unit) <= size else unit
        )
    chunks.append(current)
    return chunks

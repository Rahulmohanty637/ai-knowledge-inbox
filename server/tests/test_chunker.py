import pytest

from app.services.chunker import chunk_text, normalize_text

SENTENCES = [f"Sentence number {i} talks about topic {i}." for i in range(60)]
LONG_TEXT = " ".join(SENTENCES)


def test_empty_or_blank_text_gives_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n\n  ") == []


def test_short_text_is_one_chunk():
    assert chunk_text("Dentist on 24 Nov at 4:30 pm.") == ["Dentist on 24 Nov at 4:30 pm."]


def test_long_text_respects_size_limit():
    chunks = chunk_text(LONG_TEXT, size=200, overlap=40)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_no_sentence_is_lost():
    chunks = chunk_text(LONG_TEXT, size=200, overlap=40)
    for sentence in SENTENCES:
        assert any(sentence in c for c in chunks), sentence


def test_consecutive_chunks_overlap():
    chunks = chunk_text(LONG_TEXT, size=200, overlap=40)
    for prev, nxt in zip(chunks, chunks[1:]):
        first_word = nxt.split()[0]
        assert first_word in prev[-60:]


def test_very_long_sentence_is_hard_split():
    chunks = chunk_text("x" * 450, size=200, overlap=0)
    assert [len(c) for c in chunks] == [200, 200, 50]


def test_invalid_settings_raise():
    with pytest.raises(ValueError):
        chunk_text("hello", size=100, overlap=100)


def test_normalize_collapses_whitespace():
    assert normalize_text("a   b\r\n\r\n\r\nc  ") == "a b\n\nc"
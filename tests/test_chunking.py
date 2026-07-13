import pytest

from app.chunking import chunk_text


def test_chunk_text_preserves_content_and_overlap() -> None:
    text = " ".join(f"mot{i}" for i in range(500))
    chunks = chunk_text(text, chunk_size=220, overlap=30)
    assert len(chunks) > 1
    assert chunks[0].index == 0
    assert all(chunk.text for chunk in chunks)
    assert chunks[-1].end_char == len(text)


def test_chunk_text_empty() -> None:
    assert chunk_text("   ") == []


def test_chunk_text_rejects_bad_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=10, overlap=10)

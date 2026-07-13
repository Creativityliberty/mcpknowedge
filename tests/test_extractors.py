from pathlib import Path

import pytest

from app.extractors import UnsupportedDocumentError, extract_text


def test_extract_text_file(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("Bonjour\n\nMonde", encoding="utf-8")
    assert extract_text(path) == "Bonjour\nMonde"


def test_extract_rejects_extension(tmp_path: Path) -> None:
    path = tmp_path / "sample.xyz"
    path.write_text("test", encoding="utf-8")
    with pytest.raises(UnsupportedDocumentError):
        extract_text(path)

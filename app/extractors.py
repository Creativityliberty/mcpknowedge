from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".html", ".htm"}


class UnsupportedDocumentError(ValueError):
    pass


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentError(
            f"Format non pris en charge: {suffix}. Formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".pdf":
        reader = PdfReader(str(path))
        text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix == ".docx":
        doc = DocxDocument(str(path))
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        html = path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text("\n")

    cleaned = "\n".join(line.strip() for line in text.splitlines())
    cleaned = "\n".join(line for line in cleaned.splitlines() if line)
    if not cleaned.strip():
        raise ValueError("Aucun texte exploitable n’a été extrait du document.")
    return cleaned.strip()

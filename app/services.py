import hashlib
import mimetypes
import shutil
from pathlib import Path
from uuid import uuid4

from app.chunking import chunk_text
from app.config import Settings
from app.db import Registry
from app.embeddings import OllamaEmbeddings
from app.extractors import extract_text
from app.models import Document, SearchHit
from app.vector_store import VectorStore


class KnowledgeService:
    def __init__(
        self,
        settings: Settings,
        registry: Registry,
        embeddings: OllamaEmbeddings,
        vectors: VectorStore,
    ) -> None:
        self.settings = settings
        self.registry = registry
        self.embeddings = embeddings
        self.vectors = vectors

    def register_document(self, filename: str, content: bytes, mime_type: str | None = None) -> tuple[Document, Path, bool]:
        if not content:
            raise ValueError("Le fichier est vide")
        max_bytes = self.settings.max_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise ValueError(f"Le fichier dépasse {self.settings.max_upload_mb} Mo")

        digest = hashlib.sha256(content).hexdigest()
        existing = self.registry.get_by_hash(digest)
        if existing:
            return existing, Path(existing.storage_path), True

        document_id = str(uuid4())
        safe_name = Path(filename).name
        suffix = Path(safe_name).suffix.lower()
        storage_path = self.settings.upload_dir / f"{document_id}{suffix}"
        storage_path.write_bytes(content)
        detected_mime = mime_type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
        title = Path(safe_name).stem.replace("_", " ").replace("-", " ").strip() or safe_name

        doc = self.registry.create(
            document_id=document_id,
            filename=safe_name,
            title=title,
            mime_type=detected_mime,
            sha256=digest,
            size_bytes=len(content),
            embedding_model=self.settings.embedding_model,
            storage_path=str(storage_path),
        )
        return doc, storage_path, False

    def process_document(self, document_id: str, storage_path: Path) -> None:
        try:
            doc = self.registry.get(document_id)
            text = extract_text(storage_path)
            chunks = chunk_text(
                text,
                chunk_size=self.settings.chunk_size,
                overlap=self.settings.chunk_overlap,
            )
            if not chunks:
                raise ValueError("Le document n’a produit aucun passage indexable")
            vectors = self.embeddings.embed_documents([chunk.text for chunk in chunks])
            self.vectors.upsert_document(
                document_id=document_id,
                filename=doc.filename,
                title=doc.title,
                chunks=chunks,
                vectors=vectors,
            )
            self.registry.mark_ready(document_id, len(chunks))
        except Exception as exc:
            self.registry.mark_failed(document_id, str(exc))
            raise

    def ingest_bytes(self, filename: str, content: bytes, mime_type: str | None = None) -> Document:
        doc, storage_path, already_exists = self.register_document(filename, content, mime_type)
        if already_exists:
            return doc
        self.process_document(doc.id, storage_path)
        return self.registry.get(doc.id)

    def list_documents(self) -> list[Document]:
        return self.registry.list()

    def get_document(self, document_id: str) -> Document:
        return self.registry.get(document_id)

    def get_document_text(self, document_id: str) -> str:
        path = self.registry.get_storage_path(document_id)
        return extract_text(path)

    def search(
        self,
        query: str,
        *,
        document_id: str | None = None,
        limit: int = 8,
        score_threshold: float | None = None,
    ) -> list[SearchHit]:
        if not query.strip():
            raise ValueError("La requête est vide")
        if document_id:
            self.registry.get(document_id)
        vector = self.embeddings.embed_query(query.strip())
        return self.vectors.search(
            vector,
            document_id=document_id,
            limit=limit,
            score_threshold=score_threshold,
        )

    def delete_document(self, document_id: str) -> None:
        self.vectors.delete_document(document_id)
        path = self.registry.delete(document_id)
        if path.exists():
            path.unlink()

    def reset_all(self) -> None:
        for document in self.registry.list():
            self.delete_document(document.id)
        if self.settings.upload_dir.exists():
            for child in self.settings.upload_dir.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)

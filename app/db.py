import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

from app.models import Document


class Registry:
    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    title TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    sha256 TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    embedding_model TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error TEXT
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)")

    def create(
        self,
        *,
        document_id: str,
        filename: str,
        title: str,
        mime_type: str,
        sha256: str,
        size_bytes: int,
        embedding_model: str,
        storage_path: str,
    ) -> Document:
        now = datetime.now(UTC).isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    id, filename, title, mime_type, sha256, status, size_bytes,
                    chunk_count, embedding_model, storage_path, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'processing', ?, 0, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    filename,
                    title,
                    mime_type,
                    sha256,
                    size_bytes,
                    embedding_model,
                    storage_path,
                    now,
                    now,
                ),
            )
        return self.get(document_id)

    def get_by_hash(self, sha256: str) -> Document | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM documents WHERE sha256 = ?", (sha256,)).fetchone()
        return self._to_document(row) if row else None

    def get(self, document_id: str) -> Document:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        if not row:
            raise KeyError(f"Document introuvable: {document_id}")
        return self._to_document(row)

    def get_storage_path(self, document_id: str) -> Path:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT storage_path FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
        if not row:
            raise KeyError(f"Document introuvable: {document_id}")
        return Path(row["storage_path"])

    def list(self) -> list[Document]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
        return [self._to_document(row) for row in rows]

    def mark_ready(self, document_id: str, chunk_count: int) -> None:
        now = datetime.now(UTC).isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE documents
                SET status = 'ready', chunk_count = ?, updated_at = ?, error = NULL
                WHERE id = ?
                """,
                (chunk_count, now, document_id),
            )

    def mark_failed(self, document_id: str, error: str) -> None:
        now = datetime.now(UTC).isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE documents SET status = 'failed', error = ?, updated_at = ? WHERE id = ?
                """,
                (error[:2000], now, document_id),
            )

    def delete(self, document_id: str) -> Path:
        path = self.get_storage_path(document_id)
        with self.connect() as conn:
            conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        return path

    @staticmethod
    def _to_document(row: sqlite3.Row) -> Document:
        return Document(
            id=row["id"],
            filename=row["filename"],
            title=row["title"],
            mime_type=row["mime_type"],
            sha256=row["sha256"],
            status=row["status"],
            size_bytes=row["size_bytes"],
            chunk_count=row["chunk_count"],
            embedding_model=row["embedding_model"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            error=row["error"],
        )

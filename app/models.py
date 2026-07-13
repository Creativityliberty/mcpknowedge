from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str
    filename: str
    title: str
    mime_type: str
    sha256: str
    status: str
    size_bytes: int
    chunk_count: int = 0
    embedding_model: str
    created_at: datetime
    updated_at: datetime
    error: str | None = None


class SearchHit(BaseModel):
    document_id: str
    filename: str
    title: str
    chunk_index: int
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    document_id: str | None = None
    hits: list[SearchHit]


class HealthResponse(BaseModel):
    status: str
    qdrant: str
    ollama: str
    embedding_model: str
    mcp_url: str

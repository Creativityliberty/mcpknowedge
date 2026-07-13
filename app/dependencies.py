from functools import lru_cache

from app.config import get_settings
from app.db import Registry
from app.embeddings import OllamaEmbeddings
from app.services import KnowledgeService
from app.vector_store import VectorStore


@lru_cache

def get_registry() -> Registry:
    settings = get_settings()
    registry = Registry(settings.database_path)
    registry.initialize()
    return registry


@lru_cache

def get_embeddings() -> OllamaEmbeddings:
    settings = get_settings()
    return OllamaEmbeddings(settings.ollama_url, settings.embedding_model)


@lru_cache

def get_vector_store() -> VectorStore:
    settings = get_settings()
    return VectorStore(settings.qdrant_url, settings.qdrant_collection)


@lru_cache

def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService(
        settings=get_settings(),
        registry=get_registry(),
        embeddings=get_embeddings(),
        vectors=get_vector_store(),
    )

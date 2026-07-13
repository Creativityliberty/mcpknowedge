from uuid import uuid4

from qdrant_client import QdrantClient, models

from app.chunking import Chunk
from app.models import SearchHit


class VectorStore:
    def __init__(self, url: str, collection: str) -> None:
        self.collection = collection
        try:
            self.client = QdrantClient(url=url, timeout=2.0)
            self.client.get_collections()
        except Exception:
            import os
            os.makedirs("./data/qdrant_db", exist_ok=True)
            self.client = QdrantClient(path="./data/qdrant_db")

    def ensure_collection(self, vector_size: int) -> None:
        if self.client.collection_exists(self.collection):
            info = self.client.get_collection(self.collection)
            configured_size = info.config.params.vectors.size
            if configured_size != vector_size:
                raise RuntimeError(
                    f"Dimension Qdrant existante ({configured_size}) différente du modèle ({vector_size}). "
                    "Changez QDRANT_COLLECTION ou recréez la collection."
                )
            return
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )
        self.client.create_payload_index(
            collection_name=self.collection,
            field_name="document_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

    def upsert_document(
        self,
        *,
        document_id: str,
        filename: str,
        title: str,
        chunks: list[Chunk],
        vectors: list[list[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("Le nombre de chunks et de vecteurs diffère")
        if not vectors:
            raise ValueError("Aucun vecteur à enregistrer")
        self.ensure_collection(len(vectors[0]))
        points = [
            models.PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "title": title,
                    "chunk_index": chunk.index,
                    "text": chunk.text,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self.client.upsert(collection_name=self.collection, points=points, wait=True)

    def search(
        self,
        query_vector: list[float],
        *,
        limit: int = 8,
        document_id: str | None = None,
        score_threshold: float | None = None,
    ) -> list[SearchHit]:
        if not self.client.collection_exists(self.collection):
            return []
        query_filter = None
        if document_id:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id", match=models.MatchValue(value=document_id)
                    )
                ]
            )
        response = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            query_filter=query_filter,
            limit=max(1, min(limit, 30)),
            score_threshold=score_threshold,
            with_payload=True,
        )
        hits: list[SearchHit] = []
        for point in response.points:
            payload = point.payload or {}
            hits.append(
                SearchHit(
                    document_id=str(payload.get("document_id", "")),
                    filename=str(payload.get("filename", "")),
                    title=str(payload.get("title", "")),
                    chunk_index=int(payload.get("chunk_index", 0)),
                    text=str(payload.get("text", "")),
                    score=float(point.score),
                    metadata={
                        "start_char": payload.get("start_char"),
                        "end_char": payload.get("end_char"),
                    },
                )
            )
        return hits

    def delete_document(self, document_id: str) -> None:
        if not self.client.collection_exists(self.collection):
            return
        self.client.delete(
            collection_name=self.collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id", match=models.MatchValue(value=document_id)
                        )
                    ]
                )
            ),
            wait=True,
        )

    def health(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

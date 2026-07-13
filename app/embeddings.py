from collections.abc import Sequence

import httpx


class OllamaEmbeddings:
    def __init__(self, base_url: str, model: str, timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _embed(self, inputs: Sequence[str]) -> list[list[float]]:
        if not inputs:
            return []
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": list(inputs)},
            )
            response.raise_for_status()
            data = response.json()
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(inputs):
            raise RuntimeError("Réponse d'embedding Ollama invalide")
        return embeddings

    def embed_documents(self, texts: Sequence[str], batch_size: int = 24) -> list[list[float]]:
        result: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = [f"search_document: {text}" for text in texts[start : start + batch_size]]
            result.extend(self._embed(batch))
        return result

    def embed_query(self, query: str) -> list[float]:
        return self._embed([f"search_query: {query}"])[0]

    def health(self) -> bool:
        try:
            vector = self.embed_query("health check")
            return bool(vector)
        except Exception:
            return False

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nümtema Private Knowledge MCP"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    public_base_url: str = "http://localhost:8000"

    data_dir: Path = Path("./data")
    database_path: Path = Path("./data/registry.sqlite3")
    upload_dir: Path = Path("./data/uploads")

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "numtema_private_knowledge"

    ollama_url: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text-v2-moe"

    chunk_size: int = 1400
    chunk_overlap: int = 180
    max_upload_mb: int = 50
    api_token: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache

def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings

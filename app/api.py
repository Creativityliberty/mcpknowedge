from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from app.config import Settings, get_settings
from app.dependencies import get_embeddings, get_knowledge_service, get_vector_store
from app.embeddings import OllamaEmbeddings
from app.models import Document, HealthResponse, SearchResponse
from app.services import KnowledgeService
from app.vector_store import VectorStore


router = APIRouter()
STATIC_DIR = Path(__file__).parent / "static"


def verify_token(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if not settings.api_token:
        return
    expected = f"Bearer {settings.api_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Jeton API invalide")


@router.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/api/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(get_settings),
    embeddings: OllamaEmbeddings = Depends(get_embeddings),
    vectors: VectorStore = Depends(get_vector_store),
) -> HealthResponse:
    qdrant_ok = vectors.health()
    ollama_ok = embeddings.health()
    return HealthResponse(
        status="ok" if qdrant_ok and ollama_ok else "degraded",
        qdrant="ok" if qdrant_ok else "unreachable",
        ollama="ok" if ollama_ok else "unreachable_or_model_missing",
        embedding_model=settings.embedding_model,
        mcp_url=f"{settings.public_base_url.rstrip('/')}/mcp",
    )


@router.get("/api/documents", response_model=list[Document], dependencies=[Depends(verify_token)])
def list_documents(service: KnowledgeService = Depends(get_knowledge_service)) -> list[Document]:
    return service.list_documents()


@router.get("/api/documents/{document_id}", response_model=Document, dependencies=[Depends(verify_token)])
def get_document(
    document_id: str, service: KnowledgeService = Depends(get_knowledge_service)
) -> Document:
    try:
        return service.get_document(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/documents", response_model=Document, dependencies=[Depends(verify_token)])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    service: KnowledgeService = Depends(get_knowledge_service),
) -> Document:
    try:
        content = await file.read()
        doc, storage_path, already_exists = service.register_document(
            file.filename or "document", content, file.content_type
        )
        if not already_exists:
            background_tasks.add_task(service.process_document, doc.id, storage_path)
        return doc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Échec de l'indexation: {exc}") from exc


@router.delete("/api/documents/{document_id}", status_code=204, dependencies=[Depends(verify_token)])
def delete_document(
    document_id: str, service: KnowledgeService = Depends(get_knowledge_service)
) -> None:
    try:
        service.delete_document(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/documents/{document_id}/text", dependencies=[Depends(verify_token)])
def get_document_text(
    document_id: str, service: KnowledgeService = Depends(get_knowledge_service)
) -> dict[str, str]:
    try:
        text = service.get_document_text(document_id)
        return {"text": text}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/search", response_model=SearchResponse, dependencies=[Depends(verify_token)])
def search(
    q: str = Query(min_length=2),
    document_id: str | None = None,
    limit: int = Query(default=8, ge=1, le=30),
    service: KnowledgeService = Depends(get_knowledge_service),
) -> SearchResponse:
    try:
        hits = service.search(q, document_id=document_id, limit=limit)
        return SearchResponse(query=q, document_id=document_id, hits=hits)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

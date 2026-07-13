from typing import Any

from mcp.server.fastmcp import FastMCP

from app.config import get_settings
from app.dependencies import get_knowledge_service


settings = get_settings()
mcp = FastMCP(
    settings.app_name,
    json_response=True,
    streamable_http_path="/",
)


@mcp.tool()
def list_documents() -> list[dict[str, Any]]:
    """Liste tous les documents privés disponibles avec leur identifiant et leur URI MCP."""
    service = get_knowledge_service()
    return [
        {
            **document.model_dump(mode="json"),
            "resource_uri": f"knowledge://documents/{document.id}",
        }
        for document in service.list_documents()
    ]


@mcp.tool()
def search_knowledge(
    query: str,
    document_id: str | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Recherche les passages les plus pertinents dans toute la bibliothèque ou dans un document."""
    hits = get_knowledge_service().search(query, document_id=document_id, limit=limit)
    return [hit.model_dump(mode="json") for hit in hits]


@mcp.tool()
def inspect_document(document_id: str) -> dict[str, Any]:
    """Retourne les métadonnées, l'URI MCP et l'état d'indexation d'un document."""
    document = get_knowledge_service().get_document(document_id)
    return {
        **document.model_dump(mode="json"),
        "resource_uri": f"knowledge://documents/{document.id}",
    }


@mcp.resource("knowledge://catalog")
def knowledge_catalog() -> str:
    """Catalogue JSON de toute la bibliothèque privée."""
    documents = list_documents()
    import json

    return json.dumps(documents, ensure_ascii=False, indent=2)


@mcp.resource("knowledge://documents/{document_id}")
def document_resource(document_id: str) -> str:
    """Texte intégral extrait d'un document privé."""
    return get_knowledge_service().get_document_text(document_id)


@mcp.prompt()
def answer_from_private_knowledge(question: str, document_id: str | None = None) -> str:
    """Construit une consigne pour répondre uniquement à partir de la bibliothèque privée."""
    scope = f"le document {document_id}" if document_id else "toute la bibliothèque"
    return (
        f"Réponds à la question suivante en utilisant uniquement les passages retrouvés dans {scope}. "
        "Cite le titre du document et l'indice du passage. Signale clairement si les preuves sont insuffisantes.\n\n"
        f"Question : {question}"
    )


if __name__ == "__main__":
    mcp.run()

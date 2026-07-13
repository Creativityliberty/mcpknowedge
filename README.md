# Nümtema Private Knowledge MCP — MVP v0.1.0

Une bibliothèque de connaissances privée, locale et interrogeable par n’importe quel client compatible MCP.

## Ce que fait ce MVP

1. Vous déposez un fichier dans l’interface web.
2. Le texte est extrait puis découpé en passages.
3. Ollama génère les embeddings avec `nomic-embed-text-v2-moe`.
4. Qdrant stocke les vecteurs et les métadonnées de recherche.
5. SQLite garde le registre des documents, statuts et versions techniques.
6. Le serveur MCP expose toute la bibliothèque et chaque document individuellement.

### Accès produits

- Interface : `http://localhost:8000`
- API : `http://localhost:8000/docs`
- MCP global : `http://localhost:8000/mcp`
- Catalogue MCP : `knowledge://catalog`
- Document MCP : `knowledge://documents/{document_id}`

Le « lien MCP par document » est une ressource URI, pas un processus serveur séparé. Cela évite d’installer 50 serveurs pour 50 fichiers tout en conservant un ciblage strict par document.

## Prérequis

- Python 3.11+
- Docker et Docker Compose
- Ollama installé localement

## Démarrage local recommandé

```bash
cp .env.example .env
make install
make infra
make model
make dev
```

Ouvrez ensuite `http://localhost:8000`.

## Démarrage de l’application dans Docker

Ollama reste installé sur la machine hôte, tandis que l’application et Qdrant tournent dans Docker :

```bash
ollama pull nomic-embed-text-v2-moe
docker compose up -d --build
```

## Outils MCP disponibles

- `list_documents()` : catalogue avec identifiants et URI.
- `search_knowledge(query, document_id?, limit?)` : recherche globale ou ciblée.
- `inspect_document(document_id)` : métadonnées et état d’indexation.

## Ressources MCP

- `knowledge://catalog`
- `knowledge://documents/{document_id}`

## Exemple de configuration MCP distante

Le format exact dépend du client. Pour un client acceptant Streamable HTTP, utilisez :

```json
{
  "mcpServers": {
    "numtema-private-knowledge": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Pour vérifier avec MCP Inspector :

```bash
npx -y @modelcontextprotocol/inspector
```

Puis connectez l’Inspector à `http://localhost:8000/mcp`.

## Formats pris en charge

- PDF texte
- DOCX
- TXT
- Markdown
- HTML

Les PDF scannés nécessiteront un module OCR dans une version suivante.

## Sécurité

Par défaut, le MVP écoute localement sans authentification. Ne l’exposez pas directement sur Internet.

Pour activer un jeton Bearer sur l’API REST :

```env
API_TOKEN=une-longue-valeur-aleatoire
```

L’authentification MCP distante, les espaces utilisateurs, les ACL par document et le chiffrement au repos font partie du durcissement v0.2.

## Architecture

```text
Navigateur / IDE / ChatGPT compatible MCP
                │
        ┌───────┴────────┐
        │ FastAPI + MCP  │
        └───────┬────────┘
                │
       Ingestion / Retrieval
          │             │
      Ollama          SQLite
 Nomic Embed v2       Registre
          │
        Qdrant
   Vecteurs + payloads
```

## Vérifications

```bash
make test
make lint
```

## Limites assumées du MVP

- Indexation synchrone : l’upload attend la fin de l’embedding.
- Pas encore d’OCR.
- Pas encore de synchronisation automatique d’URL ou de dossier surveillé.
- Pas encore de reranker ni de recherche hybride lexicale + vectorielle.
- Pas encore de comptes utilisateurs/permissions granulaires.

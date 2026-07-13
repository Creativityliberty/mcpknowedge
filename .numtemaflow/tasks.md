# Morsel Tasks

### MT-001 — Initialiser le suivi projet
- Objective: Créer ou vérifier la mémoire ProjectFlow locale.
- Files: `.numtemaflow/*`
- Action: init/audit
- Verification: `python scripts/audit_projectflow.py --project .`
- Rollback: supprimer les fichiers créés seulement si demandé explicitement
- Status: done
- Updated: 2026-07-13T15:34:32+00:00

### MT-002 — Ingénierie Backend et Résilience
- Objective: Ajouter l'ingestion asynchrone, le fallback Qdrant in-process, le support stdio pour l'agent MCP, et l'endpoint de prévisualisation des documents.
- Files: `app/api.py`, `app/services.py`, `app/vector_store.py`, `app/mcp_server.py`, `Makefile`, `run_mcp.sh`
- Action: implémentation
- Status: done
- Updated: 2026-07-13T17:15:00+00:00

### MT-003 — Refonte UI (Glassmorphism & Preview)
- Objective: Intégrer une sidebar rétractable, la prévisualisation des documents extraits et un indicateur réseau.
- Files: `app/static/index.html`
- Action: implémentation
- Status: done
- Updated: 2026-07-13T17:15:00+00:00

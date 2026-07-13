# Morsel Tasks

### MT-001 — Initialiser le suivi projet
- Objective: Créer ou vérifier la mémoire ProjectFlow locale.
- Files: `.numtemaflow/*`
- Action: init/audit
- Verification: `python scripts/audit_projectflow.py --project .`
- Rollback: supprimer les fichiers créés seulement si demandé explicitement
- Status: done
- Updated: 2026-07-13T15:34:32+00:00

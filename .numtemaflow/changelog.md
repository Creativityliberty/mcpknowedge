# Changelog

## 2026-06-16
- Changed: ProjectFlow memory scaffold prepared.
- Why: Enable local project tracking and handoff.
- Files: `.numtemaflow/*`
- Verified: pending audit.

## 2026-07-13T15:33:47+00:00 — ProjectFlow init
- Created files: 13
- Skipped existing files: 0
- Detected type: python-project
- Detected stack: python, docker, docker-compose

## 2026-07-13T15:34:32+00:00 — Task lifecycle
- MT-001 — Initialiser le suivi projet -> done
- No note provided

## 2026-07-13T15:47:19+00:00 — ProjectFlow refresh
- Detected type: python-project
- Detected stack: python, docker, docker-compose
- Detected frameworks: none

## 2026-07-13T16:46:20+00:00 — Verification run
- failed: `python -m pytest`
- failed: `python -m compileall .`

## 2026-07-13T17:15:00+00:00 — Task lifecycle
- MT-002 — Ingénierie Backend et Résilience -> done
- MT-003 — Refonte UI (Glassmorphism & Preview) -> done
- All backend resilience (Qdrant fallback, FastAPI BackgroundTasks) and UI/MCP changes (Stdio, Document Preview) completed and tested.

.PHONY: install infra model dev test lint docker-up docker-down

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -e ".[dev]"

infra:
	docker compose up -d qdrant

model:
	ollama pull nomic-embed-text-v2-moe

dev:
	. .venv/bin/activate && python -m app.main

test:
	. .venv/bin/activate && pytest -q

lint:
	. .venv/bin/activate && ruff check app tests

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

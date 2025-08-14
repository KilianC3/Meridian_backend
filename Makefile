# Detect docker compose variant
DC := $(shell command -v docker-compose >/dev/null 2>&1 && echo docker-compose || echo docker compose)

.PHONY: up down fmt lint type test migrate migrate-local migrate-dc

up:
	$(DC) up -d

down:
	$(DC) down

fmt:
	poetry run pre-commit run --all-files

lint:
	poetry run ruff check .
	poetry run bandit -r app ingestion || true
	poetry run mypy app

type:
	poetry run mypy app

test:
	poetry run pytest -q

# Try local psql; if missing, run through the postgres container.
migrate: migrate-local migrate-dc

migrate-local:
	@command -v psql >/dev/null 2>&1 && \
	  (psql "$$POSTGRES_DSN" -f sql/001_init.sql && psql "$$POSTGRES_DSN" -f sql/002_indexes.sql) || true

migrate-dc:
	@command -v psql >/dev/null 2>&1 || \
	  ($(DC) exec -T postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB -f /app/sql/001_init.sql && \
	   $(DC) exec -T postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB -f /app/sql/002_indexes.sql)

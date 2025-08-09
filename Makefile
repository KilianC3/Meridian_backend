.PHONY: fmt lint test up down migrate revision

fmt:
	pre-commit run --files $(shell git ls-files '*.py') --show-diff-on-failure || true
	black app tests
	isort app tests
	ruff check --fix app tests

lint:
	ruff check app tests
	mypy app

test:
	pytest

up:
	docker-compose up --build

down:
	docker-compose down -v

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(m)"

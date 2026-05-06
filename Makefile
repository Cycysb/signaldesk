.PHONY: run test lint typecheck check up down

run:
	uv run flask --app incident_api.app:create_app run --debug

test:
	uv run pytest

lint:
	uv run ruff check .

typecheck:
	uv run mypy services tests

check: lint typecheck test

up:
	docker compose up -d

down:
	docker compose down
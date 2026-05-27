.PHONY: run test lint typecheck check up down

run:
	uv run flask --app incident_api.app:create_app run --debug

test:
	uv run pytest

test-unit:
	uv run pytest tests/unit

test-integration:
	uv run pytest tests/integration

lint:
	uv run ruff check .

typecheck:
	uv run mypy services tests

check: lint typecheck test

up:
	docker compose up -d

down:
	docker compose down

migration:
	uv run alembic revision --autogenerate -m "$(message)"

migrate:
	uv run alembic upgrade head

run-outbox-worker:
	uv run python -m incident_api.outbox_worker

run-notification-worker:
	uv run python -m incident_api.notification_worker
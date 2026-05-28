# SignalDesk

Production-style incident intelligence backend built with:

- Python
- Flask
- PostgreSQL
- Kafka
- SQLAlchemy
- Alembic
- pytest
- uv

## Features

- incident lifecycle API
- PostgreSQL persistence
- outbox pattern
- Kafka producer
- Kafka consumer
- idempotent event processing
- retry/dead-letter handling
- structured logs
- request tracing

## Architecture

See:

- docs/architecture.md
- docs/adr/
- docs/events/

## Local development

Start dependencies:

```bash
docker compose up -d
```

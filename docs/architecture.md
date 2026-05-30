# SignalDesk Architecture

## Overview

SignalDesk is a production-style incident intelligence backend built to demonstrate modern backend engineering practices with Python.

The system provides:

- incident lifecycle management
- asynchronous event publication
- Kafka-based event consumption
- durable notification task creation
- production-inspired observability and operational behavior

SignalDesk is intentionally structured as a monorepo and follows layered architecture principles to keep business logic isolated, testable, and maintainable.

---

## Technology Stack

### Backend

- Python 3.13
- Flask
- SQLAlchemy
- Alembic
- Pydantic
- pytest
- mypy
- Ruff
- uv

### Infrastructure

- PostgreSQL
- Kafka
- Docker Compose

---

## High-Level Architecture

```text
                           ┌───────────────────┐
                           │    HTTP Client    │
                           └─────────┬─────────┘
                                     │
                                     ▼
                           ┌───────────────────┐
                           │    Flask API      │
                           │  incident_api     │
                           └─────────┬─────────┘
                                     │
                          ┌──────────┴──────────┐
                          ▼                     ▼
                 ┌────────────────┐    ┌─────────────────┐
                 │ PostgreSQL DB  │    │  Outbox Events  │
                 │   incidents    │    │ outbox_events   │
                 └────────┬───────┘    └────────┬────────┘
                          │                     │
                          │                     ▼
                          │            ┌────────────────┐
                          │            │ Outbox Worker  │
                          │            └────────┬───────┘
                          │                     │
                          │                     ▼
                          │               ┌──────────┐
                          │               │  Kafka   │
                          │               └────┬─────┘
                          │                    │
                          │                    ▼
                          │          ┌──────────────────┐
                          │          │NotificationWorker│
                          │          └────────┬─────────┘
                          │                   │
                          ▼                   ▼
                ┌──────────────────┐
                │notification_tasks│
                └──────────────────┘
```

---

## Layered Architecture

SignalDesk uses a layered architecture.

```text
API Layer
    ↓
Application Layer
    ↓
Domain Layer
    ↓
Adapter Layer
    ↓
Infrastructure
```

### API Layer

Location:

```text
incident_api/api/
```

Responsibilities:

- HTTP transport
- request validation
- response serialization
- error handling

The API layer should remain thin and should not contain business logic.

Example:

```text
POST /api/v1/incidents
```

Responsibilities:

- validate JSON payload
- construct application command
- call handler
- return HTTP response

---

### Application Layer

Location:

```text
incident_api/application/
```

Responsibilities:

- orchestrate use cases
- coordinate repositories
- execute business workflows

Examples:

- CreateIncidentHandler
- ChangeIncidentSeverityHandler
- ChangeIncidentStatusHandler

The application layer coordinates behavior but should not contain transport-specific concerns.

---

### Domain Layer

Location:

```text
incident_api/domain/
```

Responsibilities:

- business rules
- invariants
- domain models
- domain events

Examples:

```text
Resolved incidents cannot change severity.
Resolved incidents cannot change status.
```

Domain rules must live here.

They must not depend on Flask, PostgreSQL, or Kafka.

---

### Adapter Layer

Location:

```text
incident_api/adapters/
```

Responsibilities:

- persistence
- repository implementation
- database mapping
- integration with infrastructure

Examples:

- IncidentRepository
- OutboxRepository
- NotificationTaskRepository

---

## Persistence Strategy

PostgreSQL is the source of truth.

The database stores:

### incidents

Primary business entity.

Contains:

- title
- severity
- status
- ownership
- timestamps

### outbox_events

Stores domain events before Kafka publication.

Purpose:

- durable event publication
- retries
- dead-letter support

### notification_tasks

Stores notification work produced by Kafka consumers.

Purpose:

- idempotent processing
- asynchronous notification delivery

---

## Event Flow

### Incident Creation

```text
POST /api/v1/incidents
    ↓
CreateIncidentHandler
    ↓
Incident domain model
    ↓
Domain event generated
    ↓
incident row persisted
    ↓
outbox event persisted
    ↓
transaction committed
```

### Event Publication

```text
Outbox worker
    ↓
load pending events
    ↓
publish to Kafka
    ↓
mark published
```

### Event Consumption

```text
Kafka consumer
    ↓
IncidentEventHandler
    ↓
notification task persisted
    ↓
offset committed
```

---

## Reliability Strategy

SignalDesk intentionally avoids publishing Kafka events directly from HTTP request handlers.

Instead:

```text
database write
+
outbox write
```

occur inside the same transaction.

This guarantees durable event publication.

Consumers are designed to be idempotent using:

```text
source_event_id UNIQUE CONSTRAINT
```

to prevent duplicate side effects.

---

## Observability

SignalDesk includes:

- structured JSON logging
- request IDs
- correlation IDs
- health endpoints
- readiness checks

Example headers:

```text
X-Request-ID
X-Correlation-ID
```

These identifiers allow request tracing across asynchronous workflows.

---

## Design Principles

SignalDesk follows these principles:

- thin HTTP layer
- explicit typing
- strong separation of concerns
- durable event publication
- idempotent consumers
- testability over convenience
- production-inspired operational behavior

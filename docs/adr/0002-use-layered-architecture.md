# ADR-0002: Use Layered Architecture

## Status

Accepted

---

## Context

The system must remain maintainable and testable as complexity grows.

We want to avoid coupling business logic to:

- Flask
- SQLAlchemy
- PostgreSQL
- Kafka

---

## Decision

Adopt layered architecture.

```text
API
↓
Application
↓
Domain
↓
Adapters
```

---

## Consequences

### Positive

- business rules remain framework-independent
- domain logic is easy to unit test
- persistence details are isolated
- Kafka workers can reuse business logic

### Negative

- additional indirection
- more files and abstractions

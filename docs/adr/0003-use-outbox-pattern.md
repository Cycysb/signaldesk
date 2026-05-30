# ADR-0003: Use Outbox Pattern

## Status

Accepted

---

## Context

Incident changes produce Kafka events.

Publishing directly to Kafka from HTTP handlers creates inconsistency risk.

Example:

```text
incident persisted
Kafka publish fails
event lost
```

---

## Decision

Store domain events in PostgreSQL inside an `outbox_events` table.

A dedicated worker publishes pending events to Kafka.

---

## Consequences

### Positive

- reliable event publication
- retry support
- dead-letter handling
- transactional consistency

### Negative

- eventual consistency
- operational complexity
- additional worker process

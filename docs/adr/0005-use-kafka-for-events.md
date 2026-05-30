# ADR-0005: Use Kafka for Events

## Status

Accepted

---

## Context

SignalDesk requires asynchronous event propagation.

Examples:

- incident created
- incident resolved
- future alert ingestion
- notification workflows

---

## Decision

Use Kafka as the event broker.

Kafka events are published through the outbox pattern.

---

## Consequences

### Positive

- decoupled architecture
- scalable consumers
- replay capability
- event-driven workflows

### Negative

- consumer idempotency required
- additional infrastructure complexity
- operational monitoring required

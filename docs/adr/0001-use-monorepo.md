# ADR-0001: Use Monorepo

## Status

Accepted

---

## Context

SignalDesk contains multiple deployable components:

- Flask API
- Outbox worker
- Notification worker
- shared business logic

These components evolve together and share common domain concepts.

---

## Decision

Use a monorepo.

All services, workers, shared domain logic, and infrastructure code live in a single repository.

---

## Consequences

### Positive

- easier local development
- simpler refactoring
- shared libraries remain easy to evolve
- single CI pipeline
- easier onboarding

### Negative

- repository size grows over time
- architectural boundaries must be enforced through discipline

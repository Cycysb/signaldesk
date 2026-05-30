# ADR-0004: Use PostgreSQL

## Status

Accepted

---

## Context

SignalDesk requires:

- transactional consistency
- relational modeling
- indexing
- durable storage

---

## Decision

Use PostgreSQL as the primary data store.

---

## Consequences

### Positive

- strong ACID guarantees
- excellent indexing support
- mature ecosystem
- JSON support where needed

### Negative

- operational overhead
- schema migrations required

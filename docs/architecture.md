# SignalDesk Architecture

## Overview

SignalDesk is a production-style incident intelligence backend.

It allows teams to:

- create incidents
- track incident lifecycle
- publish incident events
- consume events asynchronously
- create notification tasks

## Components

### Incident API

A Flask service exposing HTTP endpoints.

Responsibilities:

- validate API requests
- execute application use cases
- persist incidents in PostgreSQL
- store domain events in the outbox table

### PostgreSQL

Primary data store.

Stores:

- incidents
- outbox events
- notification tasks

### Outbox Worker

Background worker responsible for publishing pending outbox events to Kafka.

### Kafka

Event broker used to distribute incident events.

### Notification Worker

Kafka consumer that reads incident events and creates notification tasks.

## Request flow

```text
HTTP request
  ↓
Flask route
  ↓
Pydantic validation
  ↓
Application handler
  ↓
Domain model
  ↓
Repository
  ↓
PostgreSQL
```

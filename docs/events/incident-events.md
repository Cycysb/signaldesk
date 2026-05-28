# Incident events

## incident.created

Emitted when a new incident is created.

### Envelope

```json
{
  "event_id": "uuid",
  "event_type": "incident.created",
  "event_version": 1,
  "occurred_at": "2026-01-01T00:00:00Z",
  "producer": "signaldesk-incident-api",
  "correlation_id": "uuid-or-client-value",
  "aggregate": {
    "type": "incident",
    "id": "uuid"
  },
  "payload": {
    "incident_id": "uuid",
    "title": "Checkout latency",
    "severity": "sev2",
    "service_name": "checkout-api",
    "owner_team": "payments",
    "correlation_id": "uuid-or-client-value"
  }
}
```

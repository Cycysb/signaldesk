from uuid import uuid4

from incident_api.messaging.event_envelope import build_event_envelope


def test_build_event_envelope() -> None:
    event_id = uuid4()
    aggregate_id = uuid4()

    envelope = build_event_envelope(
        event_id=event_id,
        event_type="incident.created",
        aggregate_type="incident",
        aggregate_id=aggregate_id,
        occurred_at="2026-01-01T00:00:00Z",
        payload={"severity": "sev2"},
        producer="signaldesk-incident-api",
        correlation_id="corr-123",
    )

    assert envelope == {
        "event_id": str(event_id),
        "event_type": "incident.created",
        "event_version": 1,
        "occurred_at": "2026-01-01T00:00:00Z",
        "producer": "signaldesk-incident-api",
        "aggregate": {
            "type": "incident",
            "id": str(aggregate_id),
        },
        "payload": {"severity": "sev2"},
        "correlation_id": "corr-123",
    }

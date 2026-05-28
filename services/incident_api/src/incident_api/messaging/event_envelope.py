from typing import Any
from uuid import UUID


def build_event_envelope(
    *,
    event_id: UUID,
    event_type: str,
    aggregate_type: str,
    aggregate_id: UUID,
    occurred_at: object,
    payload: dict[str, object],
    producer: str,
    correlation_id: str | None,
) -> dict[str, Any]:
    return {
        "event_id": str(event_id),
        "event_type": event_type,
        "event_version": 1,
        "occurred_at": occurred_at,
        "producer": producer,
        "correlation_id": correlation_id,
        "aggregate": {
            "type": aggregate_type,
            "id": str(aggregate_id),
        },
        "payload": payload,
    }

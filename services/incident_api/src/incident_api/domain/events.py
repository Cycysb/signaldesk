from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from uuid6 import uuid7


@dataclass(frozen=True, slots=True)
class DomainEvent:
    event_id: UUID
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    occurred_at: datetime
    payload: dict[str, object]


def incident_created_event(
    *,
    incident_id: UUID,
    title: str,
    severity: str,
    service_name: str,
    owner_team: str | None,
) -> DomainEvent:
    return DomainEvent(
        event_id=uuid7(),
        event_type="incident.created",
        aggregate_type="incident",
        aggregate_id=incident_id,
        occurred_at=datetime.now(UTC),
        payload={
            "incident_id": str(incident_id),
            "title": title,
            "severity": severity,
            "service_name": service_name,
            "owner_team": owner_team,
        },
    )

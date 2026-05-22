from datetime import UTC, datetime

from sqlalchemy.orm import Session

from incident_api.adapters.incident_models import OutboxEventRow
from incident_api.domain.events import DomainEvent


class OutboxRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, event: DomainEvent) -> None:
        row = OutboxEventRow(
            id=event.event_id,
            event_type=event.event_type,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            payload=event.payload,
            status="pending",
            occurred_at=event.occurred_at,
            created_at=datetime.now(UTC),
            published_at=None,
        )

        self._session.add(row)

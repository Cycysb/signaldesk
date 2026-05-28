from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from incident_api.adapters.incident_models import OutboxEventRow
from incident_api.domain.events import DomainEvent


@dataclass(frozen=True, slots=True)
class OutboxEvent:
    id: UUID
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    payload: dict[str, object]
    occurred_at: datetime
    correlation_id: str | None


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
            correlation_id=event.correlation_id,
        )

        self._session.add(row)

    def list_pending(self, *, limit: int) -> list[OutboxEvent]:
        statement = (
            select(OutboxEventRow)
            .where(OutboxEventRow.status == "pending")
            .order_by(OutboxEventRow.created_at.asc())
            .limit(limit)
        )

        rows = self._session.scalars(statement).all()

        return [
            OutboxEvent(
                id=row.id,
                event_type=row.event_type,
                aggregate_type=row.aggregate_type,
                aggregate_id=row.aggregate_id,
                payload=row.payload,
                occurred_at=row.occurred_at,
                correlation_id=row.correlation_id,
            )
            for row in rows
        ]

    def mark_published(self, event_id: UUID) -> None:
        row = self._session.get(OutboxEventRow, event_id)

        if row is None:
            raise ValueError("Outbox event not found")

        row.status = "published"
        row.published_at = datetime.now(UTC)

    def mark_failed(self, event_id: UUID, error: str, *, max_attempts: int) -> None:
        row = self._session.get(OutboxEventRow, event_id)

        if row is None:
            raise ValueError("Outbox event not found")

        row.attempt_count += 1
        row.last_error = error[:2000]

        if row.attempt_count >= max_attempts:
            row.status = "dead_letter"
        else:
            row.status = "pending"

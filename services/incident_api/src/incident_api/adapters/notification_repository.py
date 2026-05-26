from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid6 import uuid7

from incident_api.adapters.notification_models import NotificationTaskRow


class DuplicateNotificationTaskError(Exception):
    pass


class NotificationTaskRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_for_incident_created(
        self,
        *,
        source_event_id: UUID,
        incident_id: UUID,
        title: str,
        severity: str,
        service_name: str,
    ) -> None:
        row = NotificationTaskRow(
            id=uuid7(),
            source_event_id=source_event_id,
            incident_id=incident_id,
            channel="console",
            status="pending",
            message=(f"New {severity.upper()} incident for {service_name}: {title}"),
            created_at=datetime.now(UTC),
            sent_at=None,
        )

        self._session.add(row)

        try:
            self._session.flush()
        except IntegrityError as exc:
            raise DuplicateNotificationTaskError from exc

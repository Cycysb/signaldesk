from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from incident_api.adapters.notification_repository import (
    DuplicateNotificationTaskError,
    NotificationTaskRepository,
)


class IncidentEventHandler:
    def __init__(self, session: Session) -> None:
        self._notifications = NotificationTaskRepository(session)

    def handle(self, event: dict[str, Any]) -> None:
        event_type = str(event.get("event_type"))

        if event_type == "incident.created":
            self._handle_incident_created(event)

    def _handle_incident_created(self, event: dict[str, Any]) -> None:
        event_id = UUID(str(event["event_id"]))
        aggregate = event["aggregate"]
        payload = event["payload"]

        incident_id = UUID(str(aggregate["id"]))

        try:
            self._notifications.create_for_incident_created(
                source_event_id=event_id,
                incident_id=incident_id,
                title=str(payload["title"]),
                severity=str(payload["severity"]),
                service_name=str(payload["service_name"]),
            )
        except DuplicateNotificationTaskError:
            return

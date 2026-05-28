from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from uuid6 import uuid7

from incident_api.domain.events import DomainEvent, incident_created_event


class IncidentSeverity(StrEnum):
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"


class IncidentStatus(StrEnum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


@dataclass(slots=True)
class Incident:
    id: UUID
    title: str
    description: str | None
    severity: IncidentSeverity
    status: IncidentStatus
    service_name: str
    owner_team: str | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    events: list[DomainEvent]

    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str | None,
        severity: IncidentSeverity,
        service_name: str,
        owner_team: str | None,
        correlation_id: str | None,
    ) -> "Incident":
        now = datetime.now(UTC)

        incident = cls(
            id=uuid7(),
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            service_name=service_name,
            owner_team=owner_team,
            created_at=now,
            updated_at=now,
            resolved_at=None,
            events=[],
        )

        incident.events.append(
            incident_created_event(
                incident_id=incident.id,
                title=incident.title,
                severity=incident.severity.value,
                service_name=incident.service_name,
                owner_team=incident.owner_team,
                correlation_id=correlation_id,
            )
        )

        return incident

    def change_severity(self, new_severity: IncidentSeverity) -> None:
        if self.status == IncidentStatus.RESOLVED:
            raise ValueError("Cannot change severity of a resolved incident")

        if self.severity == new_severity:
            return

        self.severity = new_severity
        self.updated_at = datetime.now(UTC)

    def change_status(self, new_status: IncidentStatus) -> None:
        if self.status == IncidentStatus.RESOLVED:
            raise ValueError("Resolved incidents cannot be changed")

        if self.status == new_status:
            return

        self.status = new_status
        self.updated_at = datetime.now(UTC)

        if new_status == IncidentStatus.RESOLVED:
            self.resolved_at = self.updated_at

    def pull_events(self) -> list[DomainEvent]:
        events = list(self.events)
        self.events.clear()
        return events

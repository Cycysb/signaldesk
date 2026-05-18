from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from uuid6 import uuid7


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

    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str | None,
        severity: IncidentSeverity,
        service_name: str,
        owner_team: str | None,
    ) -> "Incident":
        now = datetime.now(UTC)

        return cls(
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
        )

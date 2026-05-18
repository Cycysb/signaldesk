from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from incident_api.adapters.incident_repository import IncidentRepository
from incident_api.domain.incident import Incident, IncidentSeverity


@dataclass(frozen=True, slots=True)
class CreateIncidentCommand:
    title: str
    description: str | None
    severity: IncidentSeverity
    service_name: str
    owner_team: str | None


@dataclass(frozen=True, slots=True)
class CreateIncidentResult:
    id: UUID
    title: str
    severity: str
    status: str
    service_name: str
    owner_team: str | None


class CreateIncidentHandler:
    def __init__(self, session: Session) -> None:
        self._repository = IncidentRepository(session)

    def handle(self, command: CreateIncidentCommand) -> CreateIncidentResult:
        incident = Incident.create(
            title=command.title,
            description=command.description,
            severity=command.severity,
            service_name=command.service_name,
            owner_team=command.owner_team,
        )

        self._repository.add(incident)

        return CreateIncidentResult(
            id=incident.id,
            title=incident.title,
            severity=incident.severity.value,
            status=incident.status.value,
            service_name=incident.service_name,
            owner_team=incident.owner_team,
        )

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from incident_api.adapters.incident_repository import IncidentRepository
from incident_api.adapters.outbox_repository import OutboxRepository
from incident_api.domain.incident import Incident, IncidentSeverity, IncidentStatus


@dataclass(frozen=True, slots=True)
class ListIncidentsQuery:
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class ChangeIncidentSeverityCommand:
    incident_id: UUID
    severity: IncidentSeverity


@dataclass(frozen=True, slots=True)
class ChangeIncidentStatusCommand:
    incident_id: UUID
    status: IncidentStatus


@dataclass(frozen=True, slots=True)
class CreateIncidentCommand:
    title: str
    description: str | None
    severity: IncidentSeverity
    service_name: str
    owner_team: str | None
    correlation_id: str | None = None


@dataclass(frozen=True, slots=True)
class IncidentResult:
    id: UUID
    title: str
    description: str | None
    severity: str
    status: str
    service_name: str
    owner_team: str | None


class CreateIncidentHandler:
    def __init__(self, session: Session) -> None:
        self._repository = IncidentRepository(session)
        self._outbox = OutboxRepository(session)

    def handle(self, command: CreateIncidentCommand) -> IncidentResult:
        incident = Incident.create(
            title=command.title,
            description=command.description,
            severity=command.severity,
            service_name=command.service_name,
            owner_team=command.owner_team,
            correlation_id=command.correlation_id,
        )

        self._repository.add(incident)

        for event in incident.pull_events():
            self._outbox.add(event)

        return _to_result(incident)


class GetIncidentHandler:
    def __init__(self, session: Session) -> None:
        self._repository = IncidentRepository(session)

    def handle(self, incident_id: UUID) -> IncidentResult | None:
        incident = self._repository.get_by_id(incident_id)

        if incident is None:
            return None

        return _to_result(incident)


class ListIncidentsHandler:
    def __init__(self, session: Session) -> None:
        self._repository = IncidentRepository(session)

    def handle(self, query: ListIncidentsQuery) -> list[IncidentResult]:
        incidents = self._repository.list(
            limit=query.limit,
            offset=query.offset,
        )

        return [_to_result(incident) for incident in incidents]


class ChangeIncidentSeverityHandler:
    def __init__(self, session: Session) -> None:
        self._repository = IncidentRepository(session)

    def handle(self, command: ChangeIncidentSeverityCommand) -> IncidentResult | None:
        incident = self._repository.get_by_id(command.incident_id)

        if incident is None:
            return None

        incident.change_severity(command.severity)
        self._repository.save(incident)

        return _to_result(incident)


class ChangeIncidentStatusHandler:
    def __init__(self, session: Session) -> None:
        self._repository = IncidentRepository(session)

    def handle(self, command: ChangeIncidentStatusCommand) -> IncidentResult | None:
        incident = self._repository.get_by_id(command.incident_id)

        if incident is None:
            return None

        incident.change_status(command.status)
        self._repository.save(incident)

        return _to_result(incident)


def _to_result(incident: Incident) -> IncidentResult:
    return IncidentResult(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity.value,
        status=incident.status.value,
        service_name=incident.service_name,
        owner_team=incident.owner_team,
    )

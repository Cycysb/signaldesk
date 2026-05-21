from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from incident_api.adapters.incident_models import IncidentRow
from incident_api.domain.incident import Incident, IncidentSeverity, IncidentStatus


class IncidentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, incident: Incident) -> None:
        self._session.add(self._to_row(incident))

    def get_by_id(self, incident_id: UUID) -> Incident | None:
        row = self._session.get(IncidentRow, incident_id)

        if row is None:
            return None

        return self._to_domain(row)

    def list(self, *, limit: int, offset: int) -> list[Incident]:
        statement = (
            select(IncidentRow).order_by(IncidentRow.created_at.desc()).limit(limit).offset(offset)
        )

        rows = self._session.scalars(statement).all()

        return [self._to_domain(row) for row in rows]

    def save(self, incident: Incident) -> None:
        row = self._session.get(IncidentRow, incident.id)

        if row is None:
            raise ValueError("Incident does not exist")

        row.title = incident.title
        row.description = incident.description
        row.severity = incident.severity.value
        row.status = incident.status.value
        row.service_name = incident.service_name
        row.owner_team = incident.owner_team
        row.updated_at = incident.updated_at
        row.resolved_at = incident.resolved_at

    @staticmethod
    def _to_row(incident: Incident) -> IncidentRow:
        return IncidentRow(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            severity=incident.severity.value,
            status=incident.status.value,
            service_name=incident.service_name,
            owner_team=incident.owner_team,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
            resolved_at=incident.resolved_at,
        )

    @staticmethod
    def _to_domain(row: IncidentRow) -> Incident:
        return Incident(
            id=row.id,
            title=row.title,
            description=row.description,
            severity=IncidentSeverity(row.severity),
            status=IncidentStatus(row.status),
            service_name=row.service_name,
            owner_team=row.owner_team,
            created_at=row.created_at,
            updated_at=row.updated_at,
            resolved_at=row.resolved_at,
        )

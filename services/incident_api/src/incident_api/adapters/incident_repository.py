from sqlalchemy.orm import Session

from incident_api.adapters.incident_models import IncidentRow
from incident_api.domain.incident import Incident, IncidentSeverity, IncidentStatus


class IncidentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, incident: Incident) -> None:
        row = IncidentRow(
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

        self._session.add(row)

    def get_by_id(self, incident_id: str) -> Incident | None:
        row = self._session.get(IncidentRow, incident_id)

        if row is None:
            return None

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

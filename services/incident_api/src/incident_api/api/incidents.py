from typing import Any
from uuid import UUID

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from incident_api.api.dependencies import get_container
from incident_api.api.errors import (
    bad_request_response,
    not_found_response,
    validation_error_response,
)
from incident_api.api.schemas import CreateIncidentRequest, IncidentResponse
from incident_api.application.incidents import (
    CreateIncidentCommand,
    CreateIncidentHandler,
    GetIncidentHandler,
    IncidentResult,
)
from incident_api.domain.incident import IncidentSeverity
from incident_api.extensions import session_scope

incidents_bp = Blueprint("incidents", __name__, url_prefix="/api/v1/incidents")


@incidents_bp.post("")
def create_incident() -> tuple[Any, int]:
    payload = request.get_json(silent=True)

    if payload is None:
        return bad_request_response("Request body must be valid JSON")

    try:
        request_data = CreateIncidentRequest.model_validate(payload)
        command = CreateIncidentCommand(
            title=request_data.title,
            description=request_data.description,
            severity=IncidentSeverity(request_data.severity),
            service_name=request_data.service_name,
            owner_team=request_data.owner_team,
        )
    except ValidationError as exc:
        return validation_error_response(exc)
    except ValueError:
        return bad_request_response("Invalid severity")

    container = get_container()

    with session_scope(container.session_factory) as session:
        result = CreateIncidentHandler(session).handle(command)

    return jsonify(_incident_response(result).model_dump()), 201


@incidents_bp.get("/<incident_id>")
def get_incident(incident_id: str) -> tuple[Any, int]:
    try:
        parsed_incident_id = UUID(incident_id)
    except ValueError:
        return bad_request_response("Invalid incident id")

    container = get_container()

    with session_scope(container.session_factory) as session:
        result = GetIncidentHandler(session).handle(parsed_incident_id)

    if result is None:
        return not_found_response("Incident")

    return jsonify(_incident_response(result).model_dump()), 200


def _incident_response(result: IncidentResult) -> IncidentResponse:
    return IncidentResponse(
        id=str(result.id),
        title=result.title,
        description=result.description,
        severity=result.severity,
        status=result.status,
        service_name=result.service_name,
        owner_team=result.owner_team,
    )

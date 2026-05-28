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
from incident_api.api.request_context import get_correlation_id
from incident_api.api.schemas import (
    ChangeIncidentSeverityRequest,
    ChangeIncidentStatusRequest,
    CreateIncidentRequest,
    IncidentResponse,
    ListIncidentsResponse,
)
from incident_api.application.incidents import (
    ChangeIncidentSeverityCommand,
    ChangeIncidentSeverityHandler,
    ChangeIncidentStatusCommand,
    ChangeIncidentStatusHandler,
    CreateIncidentCommand,
    CreateIncidentHandler,
    GetIncidentHandler,
    IncidentResult,
    ListIncidentsHandler,
    ListIncidentsQuery,
)
from incident_api.domain.incident import IncidentSeverity, IncidentStatus
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
            correlation_id=get_correlation_id(),
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


@incidents_bp.get("")
def list_incidents() -> tuple[Any, int]:
    limit = min(int(request.args.get("limit", 50)), 100)
    offset = max(int(request.args.get("offset", 0)), 0)

    container = get_container()

    with session_scope(container.session_factory) as session:
        results = ListIncidentsHandler(session).handle(
            ListIncidentsQuery(limit=limit, offset=offset)
        )

    items = [_incident_response(result) for result in results]

    response = ListIncidentsResponse(
        items=items,
        limit=limit,
        offset=offset,
        count=len(items),
    )

    return jsonify(response.model_dump()), 200


@incidents_bp.patch("/<incident_id>/severity")
def change_incident_severity(incident_id: str) -> tuple[Any, int]:
    try:
        parsed_incident_id = UUID(incident_id)
    except ValueError:
        return bad_request_response("Invalid incident id")

    payload = request.get_json(silent=True)

    if payload is None:
        return bad_request_response("Request body must be valid JSON")

    try:
        request_data = ChangeIncidentSeverityRequest.model_validate(payload)
        command = ChangeIncidentSeverityCommand(
            incident_id=parsed_incident_id,
            severity=IncidentSeverity(request_data.severity),
        )
    except ValidationError as exc:
        return validation_error_response(exc)
    except ValueError:
        return bad_request_response("Invalid severity")

    container = get_container()

    try:
        with session_scope(container.session_factory) as session:
            result = ChangeIncidentSeverityHandler(session).handle(command)
    except ValueError as exc:
        return bad_request_response(str(exc))

    if result is None:
        return not_found_response("Incident")

    return jsonify(_incident_response(result).model_dump()), 200


@incidents_bp.patch("/<incident_id>/status")
def change_incident_status(incident_id: str) -> tuple[Any, int]:
    try:
        parsed_incident_id = UUID(incident_id)
    except ValueError:
        return bad_request_response("Invalid incident id")

    payload = request.get_json(silent=True)

    if payload is None:
        return bad_request_response("Request body must be valid JSON")

    try:
        request_data = ChangeIncidentStatusRequest.model_validate(payload)
        command = ChangeIncidentStatusCommand(
            incident_id=parsed_incident_id,
            status=IncidentStatus(request_data.status),
        )
    except ValidationError as exc:
        return validation_error_response(exc)
    except ValueError:
        return bad_request_response("Invalid status")

    container = get_container()

    try:
        with session_scope(container.session_factory) as session:
            result = ChangeIncidentStatusHandler(session).handle(command)
    except ValueError as exc:
        return bad_request_response(str(exc))

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

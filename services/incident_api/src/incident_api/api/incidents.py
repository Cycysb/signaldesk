from typing import Any

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.orm import Session, sessionmaker

from incident_api.application.incidents import CreateIncidentCommand, CreateIncidentHandler
from incident_api.domain.incident import IncidentSeverity
from incident_api.extensions import session_scope

incidents_bp = Blueprint("incidents", __name__, url_prefix="/api/v1/incidents")


@incidents_bp.post("")
def create_incident() -> tuple[Any, int]:
    payload = request.get_json(silent=True) or {}

    try:
        command = CreateIncidentCommand(
            title=str(payload["title"]),
            description=payload.get("description"),
            severity=IncidentSeverity(str(payload["severity"])),
            service_name=str(payload["service_name"]),
            owner_team=payload.get("owner_team"),
        )
    except KeyError as exc:
        return jsonify(
            {"error": "validation_error", "message": f"Missing field: {exc.args[0]}"}
        ), 400
    except ValueError as exc:
        return jsonify({"error": "validation_error", "message": str(exc)}), 400

    session_factory = current_app.config["DB_SESSION_FACTORY"]

    if not isinstance(session_factory, sessionmaker):
        return jsonify({"error": "server_error", "message": "Session factory not configured"}), 500

    with session_scope(session_factory) as session:
        if not isinstance(session, Session):
            return jsonify({"error": "server_error", "message": "Session not configured"}), 500

        result = CreateIncidentHandler(session).handle(command)

    return (
        jsonify(
            {
                "id": str(result.id),
                "title": result.title,
                "severity": result.severity,
                "status": result.status,
                "service_name": result.service_name,
                "owner_team": result.owner_team,
            }
        ),
        201,
    )

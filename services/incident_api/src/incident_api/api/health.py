from typing import Any

from flask import Blueprint, jsonify
from flask.typing import ResponseReturnValue
from sqlalchemy import text

from incident_api.api.dependencies import get_container

health_bp = Blueprint("health", __name__)


@health_bp.get("/health/live")
def live() -> ResponseReturnValue:
    return jsonify({"status": "ok"}), 200


@health_bp.get("/health/ready")
def ready() -> tuple[Any, int]:
    container = get_container()

    try:
        with container.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return jsonify({"status": "error", "checks": {"database": "down"}}), 503

    return jsonify({"status": "ok", "checks": {"database": "up"}}), 200

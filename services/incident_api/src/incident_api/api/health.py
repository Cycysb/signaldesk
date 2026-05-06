from typing import Any

from flask import Blueprint, current_app, jsonify
from flask.typing import ResponseReturnValue
from sqlalchemy import Engine, text

health_bp = Blueprint("health", __name__)


@health_bp.get("/health/live")
def live() -> ResponseReturnValue:
    return jsonify({"status": "ok"}), 200


@health_bp.get("/health/ready")
def ready() -> tuple[Any, int]:
    engine = current_app.config["DB_ENGINE"]

    if not isinstance(engine, Engine):
        return jsonify({"status": "error", "reason": "database engine not configured"}), 500

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return jsonify({"status": "error", "checks": {"database": "down"}}), 503

    return jsonify({"status": "ok", "checks": {"database": "up"}}), 200

from typing import Any

from flask import Blueprint, jsonify

from incident_api.api.dependencies import get_container

meta_bp = Blueprint("meta", __name__, url_prefix="/api/v1/meta")


@meta_bp.get("/service")
def service_info() -> tuple[Any, int]:
    settings = get_container().settings

    return (
        jsonify(
            {
                "service": settings.app_name,
                "environment": settings.environment,
                "version": "0.1.0",
            }
        ),
        200,
    )

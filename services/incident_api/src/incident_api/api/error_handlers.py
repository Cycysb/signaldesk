import logging
from typing import Any

from flask import jsonify

from incident_api.api.request_context import get_correlation_id, get_request_id

logger = logging.getLogger(__name__)


def handle_unexpected_error(error: Exception) -> tuple[Any, int]:
    logger.exception(
        "Unhandled exception",
        extra={
            "request_id": get_request_id(),
            "correlation_id": get_correlation_id(),
        },
    )

    return (
        jsonify(
            {
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "request_id": get_request_id(),
                "correlation_id": get_correlation_id(),
            }
        ),
        500,
    )

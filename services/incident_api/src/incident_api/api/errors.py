from typing import Any

from flask import jsonify
from pydantic import ValidationError

from incident_api.api.request_context import get_correlation_id, get_request_id


def error_response(
    *,
    error: str,
    message: str,
    status_code: int,
    details: object | None = None,
) -> tuple[Any, int]:
    body: dict[str, object] = {
        "error": error,
        "message": message,
        "request_id": get_request_id(),
        "correlation_id": get_correlation_id(),
    }

    if details is not None:
        body["details"] = details

    return jsonify(body), status_code


def validation_error_response(error: ValidationError) -> tuple[Any, int]:
    return error_response(
        error="validation_error",
        message="Invalid request body",
        details=error.errors(),
        status_code=400,
    )


def not_found_response(resource: str) -> tuple[Any, int]:
    return error_response(
        error="not_found",
        message=f"{resource} not found",
        status_code=404,
    )


def bad_request_response(message: str) -> tuple[Any, int]:
    return error_response(
        error="bad_request",
        message=message,
        status_code=400,
    )

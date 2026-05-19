from typing import Any

from flask import jsonify
from pydantic import ValidationError


def validation_error_response(error: ValidationError) -> tuple[Any, int]:
    return (
        jsonify(
            {
                "error": "validation_error",
                "message": "Invalid request body",
                "details": error.errors(),
            }
        ),
        400,
    )


def not_found_response(resource: str) -> tuple[Any, int]:
    return (
        jsonify(
            {
                "error": "not_found",
                "message": f"{resource} not found",
            }
        ),
        404,
    )


def bad_request_response(message: str) -> tuple[Any, int]:
    return (
        jsonify(
            {
                "error": "bad_request",
                "message": message,
            }
        ),
        400,
    )

import logging
import time

from flask import Response, g, request

from incident_api.api.request_context import get_correlation_id, get_request_id

logger = logging.getLogger(__name__)


def start_request_timer() -> None:
    g.request_started_at = time.perf_counter()


def log_request(response: Response) -> Response:
    started_at = getattr(g, "request_started_at", None)
    duration_ms = None

    if started_at is not None:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)

    logger.info(
        "HTTP request completed",
        extra={
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "request_id": get_request_id(),
            "correlation_id": get_correlation_id(),
        },
    )

    return response

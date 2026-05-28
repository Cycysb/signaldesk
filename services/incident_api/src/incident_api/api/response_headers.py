from flask import Response

from incident_api.api.request_context import get_correlation_id, get_request_id


def add_request_headers(response: Response) -> Response:
    response.headers["X-Request-ID"] = get_request_id()
    response.headers["X-Correlation-ID"] = get_correlation_id()
    return response

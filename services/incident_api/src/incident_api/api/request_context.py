from uuid import uuid4

from flask import g, request


def init_request_context() -> None:
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    correlation_id = request.headers.get("X-Correlation-ID", request_id)

    g.request_id = request_id
    g.correlation_id = correlation_id


def get_request_id() -> str:
    return str(getattr(g, "request_id", ""))


def get_correlation_id() -> str:
    return str(getattr(g, "correlation_id", ""))

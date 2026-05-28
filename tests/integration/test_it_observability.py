from flask.testing import FlaskClient


def test_response_contains_request_and_correlation_ids(client: FlaskClient) -> None:
    response = client.get(
        "/health/live",
        headers={
            "X-Request-ID": "req-test-123",
            "X-Correlation-ID": "corr-test-456",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test-123"
    assert response.headers["X-Correlation-ID"] == "corr-test-456"


def test_error_response_contains_trace_ids(client: FlaskClient) -> None:
    response = client.get(
        "/api/v1/incidents/not-a-uuid",
        headers={
            "X-Request-ID": "req-test-123",
            "X-Correlation-ID": "corr-test-456",
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["error"] == "bad_request"
    assert body["request_id"] == "req-test-123"
    assert body["correlation_id"] == "corr-test-456"

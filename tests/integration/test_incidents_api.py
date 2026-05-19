from flask.testing import FlaskClient


def test_create_incident_returns_201(client: FlaskClient) -> None:
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Checkout API latency spike",
            "description": "p95 latency is above 2s",
            "severity": "sev2",
            "service_name": "checkout-api",
            "owner_team": "payments",
        },
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["id"]
    assert body["title"] == "Checkout API latency spike"
    assert body["description"] == "p95 latency is above 2s"
    assert body["severity"] == "sev2"
    assert body["status"] == "open"
    assert body["service_name"] == "checkout-api"
    assert body["owner_team"] == "payments"


def test_get_incident_returns_created_incident(client: FlaskClient) -> None:
    create_response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Database CPU saturation",
            "description": "CPU above 95%",
            "severity": "sev1",
            "service_name": "postgres-main",
            "owner_team": "platform",
        },
    )

    created = create_response.get_json()

    response = client.get(f"/api/v1/incidents/{created['id']}")

    assert response.status_code == 200

    body = response.get_json()

    assert body["id"] == created["id"]
    assert body["title"] == "Database CPU saturation"
    assert body["severity"] == "sev1"
    assert body["status"] == "open"


def test_create_incident_rejects_invalid_severity(client: FlaskClient) -> None:
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Bad severity example",
            "description": None,
            "severity": "critical",
            "service_name": "checkout-api",
            "owner_team": "payments",
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["error"] == "bad_request"
    assert body["message"] == "Invalid severity"


def test_get_incident_returns_400_for_invalid_uuid(client: FlaskClient) -> None:
    response = client.get("/api/v1/incidents/not-a-uuid")

    assert response.status_code == 400

    body = response.get_json()

    assert body["error"] == "bad_request"


def test_get_incident_returns_404_for_missing_incident(client: FlaskClient) -> None:
    response = client.get("/api/v1/incidents/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404

    body = response.get_json()

    assert body["error"] == "not_found"

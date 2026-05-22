from flask import Flask
from flask.testing import FlaskClient
from incident_api.container import Container
from sqlalchemy import text


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


def test_list_incidents_returns_created_incidents(client: FlaskClient) -> None:
    client.post(
        "/api/v1/incidents",
        json={
            "title": "First incident",
            "description": None,
            "severity": "sev3",
            "service_name": "checkout-api",
            "owner_team": "payments",
        },
    )

    client.post(
        "/api/v1/incidents",
        json={
            "title": "Second incident",
            "description": None,
            "severity": "sev2",
            "service_name": "billing-api",
            "owner_team": "finance",
        },
    )

    response = client.get("/api/v1/incidents")

    assert response.status_code == 200

    body = response.get_json()

    assert body["count"] == 2
    assert len(body["items"]) == 2


def test_change_incident_severity(client: FlaskClient) -> None:
    create_response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Checkout latency",
            "description": None,
            "severity": "sev3",
            "service_name": "checkout-api",
            "owner_team": "payments",
        },
    )

    incident_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/v1/incidents/{incident_id}/severity",
        json={"severity": "sev1"},
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["severity"] == "sev1"


def test_change_incident_status_to_resolved(client: FlaskClient) -> None:
    create_response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Checkout latency",
            "description": None,
            "severity": "sev2",
            "service_name": "checkout-api",
            "owner_team": "payments",
        },
    )

    incident_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        json={"status": "resolved"},
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["status"] == "resolved"


def test_resolved_incident_cannot_change_severity_via_api(client: FlaskClient) -> None:
    create_response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Checkout latency",
            "description": None,
            "severity": "sev2",
            "service_name": "checkout-api",
            "owner_team": "payments",
        },
    )

    incident_id = create_response.get_json()["id"]

    client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        json={"status": "resolved"},
    )

    response = client.patch(
        f"/api/v1/incidents/{incident_id}/severity",
        json={"severity": "sev1"},
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["error"] == "bad_request"
    assert body["message"] == "Cannot change severity of a resolved incident"


def test_create_incident_writes_outbox_event(app: Flask, client: FlaskClient) -> None:
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

    container = app.config["CONTAINER"]

    assert isinstance(container, Container)

    with container.engine.connect() as connection:
        result = (
            connection.execute(
                text(
                    """
                SELECT event_type, aggregate_type, payload, status
                FROM outbox_events
                """
                )
            )
            .mappings()
            .one()
        )

    assert result["event_type"] == "incident.created"
    assert result["aggregate_type"] == "incident"
    assert result["status"] == "pending"
    assert result["payload"]["severity"] == "sev2"
    assert result["payload"]["service_name"] == "checkout-api"

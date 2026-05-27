from flask import Flask
from incident_api.container import Container
from incident_api.messaging.incident_event_handler import IncidentEventHandler
from sqlalchemy import text
from uuid6 import uuid7


def test_incident_event_handler_is_idempotent(app: Flask) -> None:
    container = app.config["CONTAINER"]

    assert isinstance(container, Container)

    incident_id = uuid7()
    event_id = uuid7()

    event = {
        "event_id": str(event_id),
        "event_type": "incident.created",
        "event_version": 1,
        "occurred_at": "2026-01-01T00:00:00Z",
        "producer": "signaldesk-incident-api",
        "aggregate": {
            "type": "incident",
            "id": str(incident_id),
        },
        "payload": {
            "title": "Checkout latency",
            "severity": "sev2",
            "service_name": "checkout-api",
        },
    }

    with container.session_factory() as session:
        IncidentEventHandler(session).handle(event)
        session.commit()

    with container.session_factory() as session:
        IncidentEventHandler(session).handle(event)
        session.commit()

    with container.engine.connect() as connection:
        count = connection.execute(text("SELECT COUNT(*) FROM notification_tasks")).scalar_one()

    assert count == 1

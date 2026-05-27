from typing import Any

from flask import Flask
from flask.testing import FlaskClient
from incident_api.config import Settings
from incident_api.container import Container
from incident_api.messaging.outbox_publisher import OutboxPublisher
from sqlalchemy import text


class FakeProducer:
    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []

    def publish(self, *, topic: str, key: str, value: dict[str, Any]) -> None:
        self.messages.append(
            {
                "topic": topic,
                "key": key,
                "value": value,
            }
        )


class FailingProducer:
    def publish(self, *, topic: str, key: str, value: dict[str, Any]) -> None:
        raise RuntimeError("Kafka unavailable")


def test_outbox_publisher_marks_events_as_published(app: Flask, client: FlaskClient) -> None:
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

    fake_producer = FakeProducer()
    settings = Settings(
        database_url=container.settings.database_url,
        kafka_bootstrap_servers="localhost:9092",
        incident_events_topic="signaldesk.incident-events",
        outbox_batch_size=100,
    )

    with container.session_factory() as session:
        publisher = OutboxPublisher(
            session=session,
            settings=settings,
            producer=fake_producer,
        )

        published_count = publisher.publish_batch()
        session.commit()

    assert published_count == 1
    assert len(fake_producer.messages) == 1

    message = fake_producer.messages[0]

    assert message["topic"] == "signaldesk.incident-events"
    assert message["value"]["event_type"] == "incident.created"
    assert message["value"]["payload"]["severity"] == "sev2"

    with container.engine.connect() as connection:
        status = connection.execute(text("SELECT status FROM outbox_events")).scalar_one()

    assert status == "published"


def test_outbox_publisher_marks_failed_event(app: Flask, client: FlaskClient) -> None:
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Checkout latency",
            "description": None,
            "severity": "sev2",
            "service_name": "checkout-api",
            "owner_team": "payments",
        },
    )

    assert response.status_code == 201

    container = app.config["CONTAINER"]

    with container.session_factory() as session:
        publisher = OutboxPublisher(
            session=session,
            settings=container.settings,
            producer=FailingProducer(),
        )

        published_count = publisher.publish_batch()
        session.commit()

    assert published_count == 0

    with container.engine.connect() as connection:
        row = (
            connection.execute(text("SELECT status, attempt_count, last_error FROM outbox_events"))
            .mappings()
            .one()
        )

    assert row["status"] == "pending"
    assert row["attempt_count"] == 1
    assert "Kafka unavailable" in row["last_error"]


def test_outbox_publisher_moves_event_to_dead_letter_after_max_attempts(
    app: Flask, client: FlaskClient
) -> None:
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Checkout latency",
            "description": None,
            "severity": "sev2",
            "service_name": "checkout-api",
            "owner_team": "payments",
        },
    )

    assert response.status_code == 201

    container = app.config["CONTAINER"]

    settings = container.settings
    settings.outbox_max_attempts = 1  # only works if Settings is mutable

    with container.session_factory() as session:
        publisher = OutboxPublisher(
            session=session,
            settings=settings,
            producer=FailingProducer(),
        )

        publisher.publish_batch()
        session.commit()

    with container.engine.connect() as connection:
        status = connection.execute(text("SELECT status FROM outbox_events")).scalar_one()

    assert status == "dead_letter"

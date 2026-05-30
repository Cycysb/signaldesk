import os
from collections.abc import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from incident_api.app import create_app
from incident_api.config import Settings
from incident_api.container import Container
from sqlalchemy import text


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    database_url = os.environ.get(
        "SIGNALDESK_TEST_DATABASE_URL",
        "postgresql+psycopg://signaldesk:signaldesk@localhost:5433/signaldesk_test",
    )

    settings = Settings(database_url=database_url)
    flask_app = create_app(settings)

    container = flask_app.config["CONTAINER"]

    if not isinstance(container, Container):
        raise RuntimeError("Container is not configured")

    with container.engine.begin() as connection:
        connection.execute(
            text(
                """
        TRUNCATE TABLE
            notification_tasks,
            outbox_events,
            incidents
        RESTART IDENTITY CASCADE
        """
            )
        )

    yield flask_app

    with container.engine.begin() as connection:
        connection.execute(
            text(
                """
        TRUNCATE TABLE
            notification_tasks,
            outbox_events,
            incidents
        RESTART IDENTITY CASCADE
        """
            )
        )


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

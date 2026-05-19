from incident_api.app import create_app
from incident_api.config import Settings


def test_live_health_returns_ok() -> None:
    settings = Settings(
        database_url="sqlite+pysqlite:///:memory:",
    )
    app = create_app(settings)

    client = app.test_client()
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_ready_health_returns_ok_when_database_is_up() -> None:
    settings = Settings(database_url="sqlite+pysqlite:///:memory:")
    app = create_app(settings)

    client = app.test_client()
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "checks": {"database": "up"},
    }

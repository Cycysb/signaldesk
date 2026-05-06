from flask import Flask

from incident_api.api.health import health_bp
from incident_api.config import Settings, get_settings
from incident_api.extensions import create_db_engine, create_session_factory
from incident_api.logging import configure_logging


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or get_settings()
    configure_logging(settings)

    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    engine = create_db_engine(settings)
    session_factory = create_session_factory(engine)

    app.config["DB_ENGINE"] = engine
    app.config["DB_SESSION_FACTORY"] = session_factory

    app.register_blueprint(health_bp)

    return app

from flask import Flask

from incident_api.api.health import health_bp
from incident_api.api.incidents import incidents_bp
from incident_api.config import Settings, get_settings
from incident_api.container import Container
from incident_api.extensions import create_db_engine, create_session_factory
from incident_api.logging import configure_logging


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or get_settings()
    configure_logging(settings)

    engine = create_db_engine(settings)
    session_factory = create_session_factory(engine)

    container = Container(
        settings=settings,
        engine=engine,
        session_factory=session_factory,
    )

    app = Flask(__name__)
    app.config["CONTAINER"] = container

    app.register_blueprint(health_bp)
    app.register_blueprint(incidents_bp)

    return app

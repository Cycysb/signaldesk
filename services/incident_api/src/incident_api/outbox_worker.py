import logging
import time

from incident_api.config import get_settings
from incident_api.extensions import create_db_engine, create_session_factory, session_scope
from incident_api.logging import configure_logging
from incident_api.messaging.kafka_producer import KafkaEventProducer
from incident_api.messaging.outbox_publisher import OutboxPublisher
from incident_api.worker_runtime import ShutdownFlag, install_shutdown_handlers

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    configure_logging(settings)

    shutdown = ShutdownFlag()
    install_shutdown_handlers(shutdown)

    engine = create_db_engine(settings)
    session_factory = create_session_factory(engine)

    producer = KafkaEventProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
    )

    logger.info("Outbox worker started")

    while not shutdown.should_stop:
        with session_scope(session_factory) as session:
            published_count = OutboxPublisher(
                session=session,
                settings=settings,
                producer=producer,
            ).publish_batch()

        if published_count == 0:
            time.sleep(settings.worker_poll_interval_seconds)

    logger.info("Outbox worker stopped")


if __name__ == "__main__":
    main()

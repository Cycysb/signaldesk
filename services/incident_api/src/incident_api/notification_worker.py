import logging
import time

from incident_api.config import get_settings
from incident_api.extensions import create_db_engine, create_session_factory, session_scope
from incident_api.logging import configure_logging
from incident_api.messaging.incident_event_handler import IncidentEventHandler
from incident_api.messaging.kafka_consumer import KafkaEventConsumer
from incident_api.worker_runtime import ShutdownFlag, install_shutdown_handlers

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    configure_logging(settings)

    shutdown = ShutdownFlag()
    install_shutdown_handlers(shutdown)

    engine = create_db_engine(settings)
    session_factory = create_session_factory(engine)

    consumer = KafkaEventConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="signaldesk-notification-worker",
        topics=[settings.incident_events_topic],
    )

    logger.info("Notification worker started")

    try:
        while not shutdown.should_stop:
            processed_any = False

            for message in consumer.poll_messages(timeout_seconds=1.0):
                with session_scope(session_factory) as session:
                    IncidentEventHandler(session).handle(message.value)

                consumer.commit()
                processed_any = True

            if not processed_any:
                time.sleep(settings.worker_poll_interval_seconds)

    finally:
        consumer.close()
        logger.info("Notification worker stopped")


if __name__ == "__main__":
    main()

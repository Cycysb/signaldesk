import logging

from incident_api.config import get_settings
from incident_api.extensions import create_db_engine, create_session_factory, session_scope
from incident_api.logging import configure_logging
from incident_api.messaging.incident_event_handler import IncidentEventHandler
from incident_api.messaging.kafka_consumer import KafkaEventConsumer

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    configure_logging(settings)

    engine = create_db_engine(settings)
    session_factory = create_session_factory(engine)

    consumer = KafkaEventConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="signaldesk-notification-worker",
        topics=[settings.incident_events_topic],
    )

    try:
        for message in consumer.poll_messages(timeout_seconds=5.0):
            with session_scope(session_factory) as session:
                IncidentEventHandler(session).handle(message.value)

            consumer.commit()

            logger.info(
                "Processed Kafka message",
                extra={"event_type": message.value.get("event_type")},
            )
    finally:
        consumer.close()


if __name__ == "__main__":
    main()

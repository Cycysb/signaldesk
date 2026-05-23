import logging

from sqlalchemy.orm import Session

from incident_api.adapters.outbox_repository import OutboxRepository
from incident_api.config import Settings
from incident_api.messaging.event_envelope import build_event_envelope
from incident_api.messaging.kafka_producer import KafkaEventProducer

logger = logging.getLogger(__name__)


class OutboxPublisher:
    def __init__(
        self,
        *,
        session: Session,
        settings: Settings,
        producer: KafkaEventProducer,
    ) -> None:
        self._outbox = OutboxRepository(session)
        self._settings = settings
        self._producer = producer

    def publish_batch(self) -> int:
        events = self._outbox.list_pending(limit=self._settings.outbox_batch_size)

        published_count = 0

        for event in events:
            envelope = build_event_envelope(
                event_id=event.id,
                event_type=event.event_type,
                aggregate_type=event.aggregate_type,
                aggregate_id=event.aggregate_id,
                occurred_at=event.occurred_at,
                payload=event.payload,
                producer=self._settings.app_name,
            )

            self._producer.publish(
                topic=self._settings.incident_events_topic,
                key=str(event.aggregate_id),
                value=envelope,
            )

            self._outbox.mark_published(event.id)
            published_count += 1

            logger.info(
                "Published outbox event",
                extra={
                    "event_id": str(event.id),
                    "event_type": event.event_type,
                    "aggregate_id": str(event.aggregate_id),
                },
            )

        return published_count

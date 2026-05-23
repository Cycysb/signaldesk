import json
from collections.abc import Mapping
from typing import Any

from confluent_kafka import Producer


class KafkaEventProducer:
    def __init__(self, *, bootstrap_servers: str) -> None:
        self._producer = Producer(
            {
                "bootstrap.servers": bootstrap_servers,
                "enable.idempotence": True,
                "acks": "all",
            }
        )

    def publish(
        self,
        *,
        topic: str,
        key: str,
        value: Mapping[str, Any],
    ) -> None:
        payload = json.dumps(value, default=str).encode("utf-8")

        self._producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=payload,
        )

        self._producer.flush()

import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from confluent_kafka import Consumer, KafkaException


@dataclass(frozen=True, slots=True)
class KafkaMessage:
    key: str | None
    value: dict[str, Any]


class KafkaEventConsumer:
    def __init__(
        self,
        *,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str],
    ) -> None:
        self._consumer = Consumer(
            {
                "bootstrap.servers": bootstrap_servers,
                "group.id": group_id,
                "enable.auto.commit": False,
                "auto.offset.reset": "earliest",
            }
        )
        self._consumer.subscribe(topics)

    def poll_messages(self, *, timeout_seconds: float = 1.0) -> Iterator[KafkaMessage]:
        message = self._consumer.poll(timeout_seconds)

        if message is None:
            return

        if message.error():
            raise KafkaException(message.error())

        raw_key = message.key()
        key = raw_key.decode("utf-8") if raw_key is not None else None

        raw_value = message.value()
        if raw_value is None:
            raise ValueError("Kafka message value is missing")

        value = json.loads(raw_value.decode("utf-8"))

        yield KafkaMessage(key=key, value=value)

    def commit(self) -> None:
        self._consumer.commit(asynchronous=False)

    def close(self) -> None:
        self._consumer.close()

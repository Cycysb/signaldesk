from typing import Any, Protocol


class EventProducer(Protocol):
    def publish(self, *, topic: str, key: str, value: dict[str, Any]) -> None: ...

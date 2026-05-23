from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "signaldesk-incident-api"
    environment: str = "local"
    log_level: str = "INFO"
    kafka_bootstrap_servers: str = "localhost:9092"
    incident_events_topic: str = "signaldesk.incident-events"
    outbox_batch_size: int = 100

    database_url: str

    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        env_prefix="SIGNALDESK_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

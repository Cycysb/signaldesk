from dataclasses import dataclass

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from incident_api.config import Settings


@dataclass(frozen=True, slots=True)
class Container:
    settings: Settings
    engine: Engine
    session_factory: sessionmaker[Session]

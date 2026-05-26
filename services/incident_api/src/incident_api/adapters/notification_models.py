from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from incident_api.adapters.db import Base


class NotificationTaskRow(Base):
    __tablename__ = "notification_tasks"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    source_event_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
    incident_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("source_event_id", name="uq_notification_tasks_source_event_id"),
        Index("ix_notification_tasks_status_created_at", "status", "created_at"),
        Index("ix_notification_tasks_incident_id", "incident_id"),
    )

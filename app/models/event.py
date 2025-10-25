from sqlalchemy import Text, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import uuid
from datetime import datetime


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    properties: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    __table_args__ = (
        Index("ix_events_occurred_at", "occurred_at"),
        Index("ix_events_user_id", "user_id"),
        Index("ix_events_event_type", "event_type"),
    )

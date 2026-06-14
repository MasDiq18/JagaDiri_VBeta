"""
JagaDiri — Model SafeGuard & Darurat
SafePing check-in harian dan SOS darurat.
"""

import uuid
from datetime import datetime, time, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SafePingConfig(Base):
    """Konfigurasi SafePing per pengguna."""

    __tablename__ = "safeping_configs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    check_in_time: Mapped[time] = mapped_column(Time, default=time(8, 0))
    response_window_minutes: Mapped[int] = mapped_column(Integer, default=120)
    escalation_to_emergency_contacts: Mapped[bool] = mapped_column(Boolean, default=True)
    escalation_to_119: Mapped[bool] = mapped_column(Boolean, default=False)
    snooze_days: Mapped[Optional[list]] = mapped_column(ARRAY(Integer), default=list)


class SafePingLog(Base):
    """Log check-in harian SafePing."""

    __tablename__ = "safeping_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    mood_score: Mapped[Optional[int]] = mapped_column(Integer)
    quick_note: Mapped[Optional[str]] = mapped_column(Text)
    escalation_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','responded','escalated_contact','escalated_119','snoozed')",
            name="valid_safeping_status",
        ),
        CheckConstraint("mood_score BETWEEN 1 AND 5", name="valid_mood_score"),
    )


class SOSEvent(Base):
    """Log aktivasi SOS darurat."""

    __tablename__ = "sos_events"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8))
    address_snapshot: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    contacts_notified: Mapped[Optional[dict]] = mapped_column(JSONB)
    service_119_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    ambulance_dispatched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolution_note: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            "status IN ('active','resolved','false_alarm')",
            name="valid_sos_status",
        ),
    )

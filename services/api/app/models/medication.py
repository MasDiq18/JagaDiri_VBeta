"""
JagaDiri — Model Farmasi & Manajemen Obat
"""

import uuid
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MedicationOrder(Base):
    """Pesanan obat."""

    __tablename__ = "medication_orders"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    prescription_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prescriptions.id")
    )
    pharmacy_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    is_auto_refill: Mapped[bool] = mapped_column(Boolean, default=False)
    total_amount: Mapped[Optional[int]] = mapped_column(Integer)
    delivery_address: Mapped[Optional[dict]] = mapped_column(JSONB)
    courier_service: Mapped[Optional[str]] = mapped_column(String(50))
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100))
    estimated_delivery: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','confirmed','processing','shipped','delivered','cancelled')",
            name="valid_order_status",
        ),
    )


class MedicationReminder(Base):
    """Jadwal minum obat (MedReminder)."""

    __tablename__ = "medication_reminders"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    medication_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[Optional[str]] = mapped_column(String(100))
    times_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    reminder_times: Mapped[Optional[list]] = mapped_column(ARRAY(Time))
    with_food: Mapped[bool] = mapped_column(Boolean, default=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class MedicationAdherenceLog(Base):
    """Log kepatuhan minum obat."""

    __tablename__ = "medication_adherence_logs"

    reminder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medication_reminders.id"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    taken_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    photo_proof_url: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','taken','skipped','late')",
            name="valid_adherence_status",
        ),
    )

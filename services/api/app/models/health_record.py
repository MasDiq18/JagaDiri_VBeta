"""
JagaDiri — Model Rekam Medis Elektronik (PHR)
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HealthRecord(Base):
    """Rekam medis utama."""

    __tablename__ = "health_records"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    record_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_record: Mapped[date] = mapped_column(Date, nullable=False)
    facility_name: Mapped[Optional[str]] = mapped_column(String(255))
    doctor_name: Mapped[Optional[str]] = mapped_column(String(255))
    findings: Mapped[Optional[str]] = mapped_column(Text)
    file_urls: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    is_shared_with_family: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[Optional[list]] = mapped_column(ARRAY(Text))

    __table_args__ = (
        CheckConstraint(
            "record_type IN ('lab_result','radiology','vaccination','surgery',"
            "'hospitalization','screening','document','other')",
            name="valid_record_type",
        ),
    )


class VaccinationRecord(Base):
    """Riwayat vaksinasi."""

    __tablename__ = "vaccination_records"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    vaccine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vaccine_type: Mapped[Optional[str]] = mapped_column(String(100))
    dose_number: Mapped[int] = mapped_column(Integer, default=1)
    administered_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_due_date: Mapped[Optional[date]] = mapped_column(Date)
    facility_name: Mapped[Optional[str]] = mapped_column(String(255))
    batch_number: Mapped[Optional[str]] = mapped_column(String(100))
    administrator_name: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class VitalSign(Base):
    """Data vital signs."""

    __tablename__ = "vital_signs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    value_numeric: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    value_systolic: Mapped[Optional[int]] = mapped_column(Integer)
    value_diastolic: Mapped[Optional[int]] = mapped_column(Integer)
    value_text: Mapped[Optional[str]] = mapped_column(String(255))
    unit: Mapped[Optional[str]] = mapped_column(String(30))
    source: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

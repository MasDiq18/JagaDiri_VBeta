"""
JagaDiri — Model Dokter & Konsultasi
"""

import uuid
from datetime import datetime, time as dt_time
from typing import Optional, List

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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Doctor(Base):
    """Profil dokter."""

    __tablename__ = "doctors"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    str_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    sip_number: Mapped[str] = mapped_column(String(50), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sub_specialization: Mapped[Optional[str]] = mapped_column(String(100))
    education: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    experience_years: Mapped[Optional[int]] = mapped_column(Integer)
    languages: Mapped[Optional[list]] = mapped_column(ARRAY(Text), default=lambda: ["Indonesian"])
    consultation_fee_general: Mapped[Optional[int]] = mapped_column(Integer)
    consultation_fee_specialist: Mapped[Optional[int]] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    available_for_home_visit: Mapped[bool] = mapped_column(Boolean, default=False)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    profile_photo_url: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    user: Mapped["User"] = relationship("User", lazy="selectin")
    schedules: Mapped[List["DoctorSchedule"]] = relationship(
        back_populates="doctor", lazy="selectin"
    )


class DoctorSchedule(Base):
    """Jadwal ketersediaan dokter."""

    __tablename__ = "doctor_schedules"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), index=True
    )
    day_of_week: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[dt_time] = mapped_column(Time, nullable=False)
    end_time: Mapped[dt_time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    doctor: Mapped["Doctor"] = relationship(back_populates="schedules")

    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="valid_day_of_week"),
    )


class Consultation(Base):
    """Sesi konsultasi."""

    __tablename__ = "consultations"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id"), index=True
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    chief_complaint: Mapped[str] = mapped_column(Text, nullable=False)
    patient_notes: Mapped[Optional[str]] = mapped_column(Text)
    is_urgent: Mapped[bool] = mapped_column(Boolean, default=False)
    agora_channel_name: Mapped[Optional[str]] = mapped_column(String(100))
    fee_charged: Mapped[Optional[int]] = mapped_column(Integer)
    payment_status: Mapped[str] = mapped_column(String(20), default="pending")

    # Relationships
    patient: Mapped["User"] = relationship("User", foreign_keys=[patient_id], lazy="selectin")
    doctor: Mapped["Doctor"] = relationship("Doctor", lazy="selectin")
    notes: Mapped[Optional["ConsultationNote"]] = relationship(
        back_populates="consultation", uselist=False, lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint(
            "type IN ('chat','video','home_visit','phone')",
            name="valid_consultation_type",
        ),
        CheckConstraint(
            "status IN ('pending','confirmed','ongoing','completed','cancelled','no_show')",
            name="valid_consultation_status",
        ),
    )


class ConsultationNote(Base):
    """Catatan konsultasi dokter (SOAP format)."""

    __tablename__ = "consultation_notes"

    consultation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("consultations.id"), unique=True
    )
    subjective: Mapped[Optional[str]] = mapped_column(Text)
    objective: Mapped[Optional[str]] = mapped_column(Text)
    assessment: Mapped[Optional[str]] = mapped_column(Text)
    plan: Mapped[Optional[str]] = mapped_column(Text)
    diagnosis_codes: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    follow_up_days: Mapped[Optional[int]] = mapped_column(Integer)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    consultation: Mapped["Consultation"] = relationship(back_populates="notes")

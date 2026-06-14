"""
JagaDiri — Model Resep & Farmasi
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
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Prescription(Base):
    """Resep elektronik."""

    __tablename__ = "prescriptions"

    consultation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("consultations.id"), index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id"), index=True
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    prescription_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    valid_until: Mapped[Optional[date]] = mapped_column(Date)
    notes_for_pharmacist: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    items: Mapped[list["PrescriptionItem"]] = relationship(
        back_populates="prescription", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active','dispensed','expired','cancelled')",
            name="valid_prescription_status",
        ),
    )


class PrescriptionItem(Base):
    """Item dalam resep."""

    __tablename__ = "prescription_items"

    prescription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True
    )
    medication_name: Mapped[str] = mapped_column(String(255), nullable=False)
    generic_name: Mapped[Optional[str]] = mapped_column(String(255))
    strength: Mapped[Optional[str]] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    dosage_instruction: Mapped[str] = mapped_column(Text, nullable=False)
    duration_days: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    prescription: Mapped["Prescription"] = relationship(back_populates="items")

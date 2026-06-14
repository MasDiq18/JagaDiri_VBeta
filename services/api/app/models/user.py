"""
JagaDiri — Model Pengguna & Autentikasi
"""

import uuid
from datetime import date, datetime
from typing import Optional, List

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
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """Pengguna utama platform."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    nik: Mapped[Optional[str]] = mapped_column(String(16), unique=True)
    profile_photo_url: Mapped[Optional[str]] = mapped_column(Text)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_tier: Mapped[str] = mapped_column(
        String(20), default="basic"
    )
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    medical_profile: Mapped[Optional["UserMedicalProfile"]] = relationship(
        back_populates="user", uselist=False, lazy="selectin"
    )
    emergency_contacts: Mapped[List["EmergencyContact"]] = relationship(
        back_populates="user", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint(
            "gender IN ('male', 'female', 'other')",
            name="valid_gender",
        ),
        CheckConstraint(
            "subscription_tier IN ('basic','essential','complete','premium','lansia','perempuan')",
            name="valid_subscription_tier",
        ),
    )


class UserMedicalProfile(Base):
    """Profil medis pengguna."""

    __tablename__ = "user_medical_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    blood_type: Mapped[Optional[str]] = mapped_column(String(5))
    height_cm: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    weight_kg: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    allergies: Mapped[Optional[list]] = mapped_column(ARRAY(Text), default=list)
    chronic_conditions: Mapped[Optional[list]] = mapped_column(ARRAY(Text), default=list)
    current_medications: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    emergency_contact_relation: Mapped[Optional[str]] = mapped_column(String(100))
    bpjs_number: Mapped[Optional[str]] = mapped_column(String(20))
    insurance_provider: Mapped[Optional[str]] = mapped_column(String(100))
    insurance_policy_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="medical_profile")


class EmergencyContact(Base):
    """Kontak darurat pengguna (hingga 5 kontak)."""

    __tablename__ = "emergency_contacts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    relation: Mapped[Optional[str]] = mapped_column(String(100))
    priority: Mapped[int] = mapped_column(Integer, default=1)
    can_view_health_status: Mapped[bool] = mapped_column(Boolean, default=False)
    can_view_medications: Mapped[bool] = mapped_column(Boolean, default=False)
    can_view_consultation_history: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="emergency_contacts")

    __table_args__ = (
        CheckConstraint("priority BETWEEN 1 AND 5", name="valid_priority"),
    )


class RefreshToken(Base):
    """Refresh tokens untuk manajemen sesi."""

    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    device_info: Mapped[Optional[dict]] = mapped_column(JSONB)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

"""
JagaDiri — Model Komunitas & Sosial
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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SupportGroup(Base):
    """Grup support komunitas."""

    __tablename__ = "support_groups"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    facilitator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    max_members: Mapped[int] = mapped_column(Integer, default=20)
    meeting_schedule: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    member_count: Mapped[int] = mapped_column(Integer, default=0)


class BuddyPair(Base):
    """Buddy system pasangan."""

    __tablename__ = "buddy_pairs"

    user_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    user_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="pending")
    shared_goals: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("user_a_id", "user_b_id", name="unique_buddy_pair"),
        CheckConstraint(
            "status IN ('pending','active','ended')",
            name="valid_buddy_status",
        ),
    )


class BloodDonor(Base):
    """Pendaftaran donor darah."""

    __tablename__ = "blood_donors"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True
    )
    blood_type: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    last_donation_date: Mapped[Optional[date]] = mapped_column(Date)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8))
    total_donations: Mapped[int] = mapped_column(Integer, default=0)

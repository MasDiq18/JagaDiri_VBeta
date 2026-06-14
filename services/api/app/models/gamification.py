"""
JagaDiri — Model Gamifikasi & Engagement
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserGamification(Base):
    """Poin dan level pengguna."""

    __tablename__ = "user_gamification"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True
    )
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    current_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date)
    level: Mapped[int] = mapped_column(Integer, default=1)
    badges: Mapped[Optional[list]] = mapped_column(ARRAY(Text), default=list)


class PointTransaction(Base):
    """Riwayat perolehan poin."""

    __tablename__ = "point_transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class HealthGoal(Base):
    """Target kesehatan pengguna."""

    __tablename__ = "health_goals"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    goal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_value: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    current_value: Mapped[float] = mapped_column(Numeric(10, 4), default=0)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="active")
    doctor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id")
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active','achieved','abandoned')",
            name="valid_goal_status",
        ),
    )

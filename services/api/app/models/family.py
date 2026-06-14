"""
JagaDiri — Model Portal Keluarga
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FamilyConnection(Base):
    """Koneksi keluarga/caregiver."""

    __tablename__ = "family_connections"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    family_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    relation: Mapped[Optional[str]] = mapped_column(String(100))
    access_level: Mapped[str] = mapped_column(String(20), default="basic")
    can_view_safeping: Mapped[bool] = mapped_column(Boolean, default=True)
    can_view_medication_adherence: Mapped[bool] = mapped_column(Boolean, default=True)
    can_view_vital_signs: Mapped[bool] = mapped_column(Boolean, default=False)
    can_view_consultation_history: Mapped[bool] = mapped_column(Boolean, default=False)
    can_view_mental_health: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("user_id", "family_member_id", name="unique_family_connection"),
        CheckConstraint(
            "access_level IN ('basic','standard','full')",
            name="valid_access_level",
        ),
        CheckConstraint(
            "status IN ('pending','active','revoked')",
            name="valid_connection_status",
        ),
    )

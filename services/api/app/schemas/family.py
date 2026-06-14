"""
JagaDiri — Schema Portal Keluarga
Schemas untuk koneksi keluarga, undangan, dan izin akses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class FamilyConnectionResponse(BaseModel):
    """Respons data koneksi keluarga."""

    id: UUID
    user_id: UUID
    family_member_id: UUID
    relation: Optional[str] = None
    access_level: str
    can_view_safeping: bool
    can_view_medication_adherence: bool
    can_view_vital_signs: bool
    can_view_consultation_history: bool
    can_view_mental_health: bool
    status: str
    connected_at: Optional[datetime] = None
    family_member_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FamilyInviteRequest(BaseModel):
    """Permintaan undangan koneksi keluarga."""

    email: EmailStr = Field(..., description="Email anggota keluarga yang ingin diundang")
    relation: Optional[str] = Field(
        None, max_length=100,
        description="Hubungan keluarga (misal: Anak, Orang Tua, Pasangan)",
    )
    access_level: str = Field(
        default="basic",
        description="Level akses: basic, standard, full",
    )
    can_view_safeping: bool = Field(default=True, description="Izinkan melihat status SafePing")
    can_view_medication_adherence: bool = Field(
        default=True, description="Izinkan melihat kepatuhan obat"
    )
    can_view_vital_signs: bool = Field(
        default=False, description="Izinkan melihat tanda vital"
    )
    can_view_consultation_history: bool = Field(
        default=False, description="Izinkan melihat riwayat konsultasi"
    )
    can_view_mental_health: bool = Field(
        default=False, description="Izinkan melihat data kesehatan mental"
    )

    @field_validator("access_level")
    @classmethod
    def validate_access_level(cls, v: str) -> str:
        if v not in ("basic", "standard", "full"):
            raise ValueError("Level akses harus: basic, standard, atau full")
        return v


class FamilyPermissionUpdate(BaseModel):
    """Permintaan pembaruan izin koneksi keluarga."""

    access_level: Optional[str] = Field(None, description="Level akses baru")
    can_view_safeping: Optional[bool] = None
    can_view_medication_adherence: Optional[bool] = None
    can_view_vital_signs: Optional[bool] = None
    can_view_consultation_history: Optional[bool] = None
    can_view_mental_health: Optional[bool] = None

    @field_validator("access_level")
    @classmethod
    def validate_access_level(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("basic", "standard", "full"):
            raise ValueError("Level akses harus: basic, standard, atau full")
        return v


class FamilyMemberStatusResponse(BaseModel):
    """Respons status anggota keluarga (dilihat oleh keluarga)."""

    user_id: UUID
    full_name: str
    safeping_status: Optional[str] = Field(None, description="Status SafePing terakhir")
    last_check_in: Optional[datetime] = Field(None, description="Waktu check-in terakhir")
    medication_adherence_pct: Optional[float] = Field(
        None, description="Persentase kepatuhan obat (%)"
    )
    last_vital_signs: Optional[dict] = Field(None, description="Tanda vital terakhir")
    pesan: str = Field(
        default="Data ini dibagikan oleh anggota keluarga Anda untuk pemantauan.",
    )

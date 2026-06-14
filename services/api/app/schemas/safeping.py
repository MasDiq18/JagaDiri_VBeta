"""
JagaDiri — Schema SafeGuard & Darurat
Schemas untuk SafePing check-in, konfigurasi, dan SOS darurat.
"""

from datetime import datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── SafePing Config ──────────────────────────────────────────────────────────


class SafePingConfigResponse(BaseModel):
    """Respons konfigurasi SafePing pengguna."""

    id: UUID
    user_id: UUID
    is_enabled: bool
    check_in_time: time
    response_window_minutes: int
    escalation_to_emergency_contacts: bool
    escalation_to_119: bool
    snooze_days: Optional[List[int]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SafePingConfigUpdate(BaseModel):
    """Permintaan pembaruan konfigurasi SafePing."""

    is_enabled: Optional[bool] = Field(None, description="Aktifkan/nonaktifkan SafePing")
    check_in_time: Optional[time] = Field(
        None, description="Waktu check-in harian (format: HH:MM)"
    )
    response_window_minutes: Optional[int] = Field(
        None, ge=15, le=480,
        description="Jendela waktu respons dalam menit (15-480)",
    )
    escalation_to_emergency_contacts: Optional[bool] = Field(
        None, description="Eskalasi ke kontak darurat jika tidak merespons"
    )
    escalation_to_119: Optional[bool] = Field(
        None, description="Eskalasi ke 119 jika tidak merespons"
    )
    snooze_days: Optional[List[int]] = Field(
        None, description="Hari yang di-snooze (0=Senin, 6=Minggu)",
    )

    @field_validator("snooze_days")
    @classmethod
    def validate_snooze_days(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError("Hari snooze harus antara 0 (Senin) dan 6 (Minggu)")
        return v


# ── Check-In ─────────────────────────────────────────────────────────────────


class CheckInRequest(BaseModel):
    """Permintaan check-in harian SafePing."""

    mood_score: Optional[int] = Field(
        None, ge=1, le=5,
        description="Skor suasana hati (1=Sangat Buruk, 5=Sangat Baik)",
    )
    quick_note: Optional[str] = Field(
        None, max_length=500,
        description="Catatan singkat tentang kondisi hari ini",
    )


class CheckInResponse(BaseModel):
    """Respons check-in berhasil."""

    id: UUID
    user_id: UUID
    scheduled_at: datetime
    responded_at: Optional[datetime] = None
    status: str
    mood_score: Optional[int] = None
    quick_note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckInHistoryResponse(BaseModel):
    """Respons riwayat check-in."""

    id: UUID
    user_id: UUID
    scheduled_at: datetime
    responded_at: Optional[datetime] = None
    status: str
    mood_score: Optional[int] = None
    quick_note: Optional[str] = None
    escalation_sent_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── SOS ──────────────────────────────────────────────────────────────────────


class SOSRequest(BaseModel):
    """Permintaan aktivasi SOS darurat."""

    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude lokasi")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude lokasi")
    address_snapshot: Optional[str] = Field(
        None, max_length=500, description="Alamat saat ini (teks)"
    )


class SOSResponse(BaseModel):
    """Respons SOS darurat."""

    id: UUID
    user_id: UUID
    triggered_at: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address_snapshot: Optional[str] = None
    status: str
    contacts_notified: Optional[Dict[str, Any]] = None
    service_119_notified: bool
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SOSResolveRequest(BaseModel):
    """Permintaan penyelesaian SOS."""

    status: str = Field(
        ..., description="Status penyelesaian: resolved atau false_alarm"
    )
    resolution_note: Optional[str] = Field(
        None, max_length=1000,
        description="Catatan penyelesaian kejadian",
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ("resolved", "false_alarm"):
            raise ValueError("Status harus 'resolved' atau 'false_alarm'")
        return v

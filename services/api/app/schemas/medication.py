"""
JagaDiri — Schema Pengingat Obat & Kepatuhan
Schemas untuk medication reminders, adherence logging, dan laporan.
"""

from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Medication Reminder ──────────────────────────────────────────────────────


class MedicationReminderCreate(BaseModel):
    """Permintaan pembuatan pengingat obat."""

    medication_name: str = Field(
        ..., min_length=2, max_length=255,
        description="Nama obat",
    )
    dosage: Optional[str] = Field(None, max_length=100, description="Dosis (misal: 500mg)")
    times_per_day: int = Field(
        ..., ge=1, le=10,
        description="Frekuensi minum per hari",
    )
    reminder_times: Optional[List[time]] = Field(
        None,
        description="Waktu pengingat (format HH:MM). Jumlah harus sesuai times_per_day.",
    )
    with_food: bool = Field(default=False, description="Diminum bersamaan makanan")
    start_date: date = Field(..., description="Tanggal mulai minum obat")
    end_date: Optional[date] = Field(None, description="Tanggal selesai (opsional untuk obat jangka panjang)")
    notes: Optional[str] = Field(None, max_length=500, description="Catatan tambahan")

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        if v is not None:
            start = info.data.get("start_date")
            if start and v < start:
                raise ValueError("Tanggal selesai harus setelah tanggal mulai")
        return v


class MedicationReminderUpdate(BaseModel):
    """Permintaan pembaruan pengingat obat."""

    medication_name: Optional[str] = Field(None, min_length=2, max_length=255)
    dosage: Optional[str] = Field(None, max_length=100)
    times_per_day: Optional[int] = Field(None, ge=1, le=10)
    reminder_times: Optional[List[time]] = None
    with_food: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class MedicationReminderResponse(BaseModel):
    """Respons data pengingat obat."""

    id: UUID
    user_id: UUID
    medication_name: str
    dosage: Optional[str] = None
    times_per_day: int
    reminder_times: Optional[List[time]] = None
    with_food: bool
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Adherence Logging ────────────────────────────────────────────────────────


class MedicationTakenRequest(BaseModel):
    """Konfirmasi bahwa obat sudah diminum."""

    notes: Optional[str] = Field(None, max_length=500, description="Catatan tambahan")
    photo_proof_url: Optional[str] = Field(None, description="URL foto bukti minum obat")


class AdherenceLogResponse(BaseModel):
    """Respons log kepatuhan minum obat."""

    id: UUID
    reminder_id: UUID
    user_id: UUID
    scheduled_at: datetime
    taken_at: Optional[datetime] = None
    status: str
    photo_proof_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Laporan Kepatuhan ────────────────────────────────────────────────────────


class AdherenceReportResponse(BaseModel):
    """Respons laporan kepatuhan minum obat."""

    user_id: UUID
    periode_awal: date
    periode_akhir: date
    total_jadwal: int = Field(..., description="Total jadwal minum obat")
    total_diminum: int = Field(..., description="Total obat yang diminum")
    total_dilewati: int = Field(..., description="Total obat yang dilewati")
    total_terlambat: int = Field(..., description="Total obat yang terlambat")
    persentase_kepatuhan: float = Field(..., description="Persentase kepatuhan (%)")
    detail_per_obat: List["AdherencePerMedication"] = Field(
        default_factory=list, description="Detail kepatuhan per obat"
    )


class AdherencePerMedication(BaseModel):
    """Detail kepatuhan per obat."""

    reminder_id: UUID
    medication_name: str
    total_jadwal: int
    total_diminum: int
    persentase: float


# Update forward reference
AdherenceReportResponse.model_rebuild()

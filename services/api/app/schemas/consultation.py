"""
JagaDiri — Schema Konsultasi & Dokter
Schemas untuk dokter, jadwal, konsultasi, catatan SOAP, dan rating.
"""

from datetime import datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Dokter ───────────────────────────────────────────────────────────────────


class DoctorScheduleResponse(BaseModel):
    """Respons jadwal dokter."""

    id: UUID
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DoctorResponse(BaseModel):
    """Respons profil dokter."""

    id: UUID
    user_id: UUID
    str_number: str
    sip_number: str
    specialization: str
    sub_specialization: Optional[str] = None
    education: Optional[List[str]] = None
    experience_years: Optional[int] = None
    languages: Optional[List[str]] = None
    consultation_fee_general: Optional[int] = None
    consultation_fee_specialist: Optional[int] = None
    rating: float
    total_reviews: int
    is_verified: bool
    is_online: bool
    available_for_home_visit: bool
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    full_name: Optional[str] = None
    schedules: List[DoctorScheduleResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorListFilter(BaseModel):
    """Filter pencarian dokter."""

    specialization: Optional[str] = Field(None, description="Spesialisasi dokter")
    is_online: Optional[bool] = Field(None, description="Hanya tampilkan dokter yang sedang online")
    available_for_home_visit: Optional[bool] = Field(None, description="Tersedia untuk kunjungan rumah")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Rating minimum")
    max_fee: Optional[int] = Field(None, ge=0, description="Biaya konsultasi maksimum (Rupiah)")
    search: Optional[str] = Field(None, description="Cari berdasarkan nama atau spesialisasi")
    halaman: int = Field(default=1, ge=1, description="Halaman")
    per_halaman: int = Field(default=10, ge=1, le=50, description="Jumlah per halaman")


# ── Konsultasi ───────────────────────────────────────────────────────────────


class ConsultationCreate(BaseModel):
    """Permintaan pembuatan konsultasi baru."""

    doctor_id: UUID = Field(..., description="ID dokter yang dituju")
    type: str = Field(..., description="Tipe konsultasi: chat, video, home_visit, phone")
    scheduled_at: Optional[datetime] = Field(None, description="Jadwal konsultasi (jika terjadwal)")
    chief_complaint: str = Field(
        ..., min_length=10, max_length=2000,
        description="Keluhan utama pasien",
    )
    patient_notes: Optional[str] = Field(
        None, max_length=2000, description="Catatan tambahan dari pasien"
    )
    is_urgent: bool = Field(default=False, description="Apakah konsultasi darurat")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid_types = {"chat", "video", "home_visit", "phone"}
        if v not in valid_types:
            raise ValueError(f"Tipe konsultasi tidak valid. Pilih: {', '.join(valid_types)}")
        return v


class ConsultationResponse(BaseModel):
    """Respons data konsultasi."""

    id: UUID
    patient_id: UUID
    doctor_id: UUID
    type: str
    status: str
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    chief_complaint: str
    patient_notes: Optional[str] = None
    is_urgent: bool
    agora_channel_name: Optional[str] = None
    fee_charged: Optional[int] = None
    payment_status: str
    doctor_name: Optional[str] = None
    patient_name: Optional[str] = None
    specialization: Optional[str] = None
    notes: Optional["ConsultationNoteResponse"] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsultationStatusUpdate(BaseModel):
    """Permintaan pembaruan status konsultasi."""

    status: str = Field(
        ..., description="Status baru: confirmed, ongoing, completed, cancelled, no_show"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = {"confirmed", "ongoing", "completed", "cancelled", "no_show"}
        if v not in valid:
            raise ValueError(f"Status tidak valid. Pilih: {', '.join(valid)}")
        return v


# ── Catatan Konsultasi (SOAP) ────────────────────────────────────────────────


class ConsultationNoteCreate(BaseModel):
    """Permintaan penambahan catatan konsultasi (format SOAP)."""

    subjective: Optional[str] = Field(None, description="Keluhan subjektif pasien (S)")
    objective: Optional[str] = Field(None, description="Pemeriksaan objektif (O)")
    assessment: Optional[str] = Field(None, description="Penilaian/diagnosis (A)")
    plan: Optional[str] = Field(None, description="Rencana tindakan (P)")
    diagnosis_codes: Optional[List[str]] = Field(None, description="Kode diagnosis ICD-10")
    follow_up_days: Optional[int] = Field(None, ge=1, description="Kontrol ulang dalam X hari")
    is_confidential: bool = Field(default=False, description="Catatan bersifat rahasia")


class ConsultationNoteResponse(BaseModel):
    """Respons catatan konsultasi."""

    id: UUID
    consultation_id: UUID
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    diagnosis_codes: Optional[List[str]] = None
    follow_up_days: Optional[int] = None
    is_confidential: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Rating ───────────────────────────────────────────────────────────────────


class RateRequest(BaseModel):
    """Permintaan pemberian rating konsultasi."""

    rating: int = Field(..., ge=1, le=5, description="Rating dokter (1-5 bintang)")
    review: Optional[str] = Field(None, max_length=1000, description="Ulasan tertulis")


# Update forward reference
ConsultationResponse.model_rebuild()

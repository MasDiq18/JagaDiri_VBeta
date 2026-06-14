"""
JagaDiri — Schema Pengguna & Profil
Schemas untuk profil pengguna, profil medis, kontak darurat, dan MedCard.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ── Profil Pengguna ──────────────────────────────────────────────────────────


class UserResponse(BaseModel):
    """Respons data pengguna lengkap."""

    id: UUID
    email: str
    phone: Optional[str] = None
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nik: Optional[str] = None
    profile_photo_url: Optional[str] = None
    onboarding_completed: bool
    is_active: bool
    is_verified: bool
    subscription_tier: str
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    """Permintaan pembaruan profil pengguna."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=255, description="Nama lengkap")
    phone: Optional[str] = Field(None, max_length=20, description="Nomor telepon")
    date_of_birth: Optional[date] = Field(None, description="Tanggal lahir")
    gender: Optional[str] = Field(None, description="Jenis kelamin")
    nik: Optional[str] = Field(None, max_length=16, description="Nomor Induk Kependudukan (NIK)")
    profile_photo_url: Optional[str] = Field(None, description="URL foto profil")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("male", "female", "other"):
            raise ValueError("Jenis kelamin harus salah satu dari: male, female, other")
        return v

    @field_validator("nik")
    @classmethod
    def validate_nik(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (len(v) != 16 or not v.isdigit()):
            raise ValueError("NIK harus terdiri dari 16 digit angka")
        return v


# ── Profil Medis ─────────────────────────────────────────────────────────────


class MedicalProfileResponse(BaseModel):
    """Respons profil medis pengguna."""

    id: UUID
    user_id: UUID
    blood_type: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    current_medications: Optional[Any] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    bpjs_number: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicalProfileUpdate(BaseModel):
    """Permintaan pembaruan profil medis."""

    blood_type: Optional[str] = Field(
        None, description="Golongan darah (A+, A-, B+, B-, AB+, AB-, O+, O-)"
    )
    height_cm: Optional[float] = Field(None, gt=0, le=300, description="Tinggi badan dalam cm")
    weight_kg: Optional[float] = Field(None, gt=0, le=500, description="Berat badan dalam kg")
    allergies: Optional[List[str]] = Field(None, description="Daftar alergi")
    chronic_conditions: Optional[List[str]] = Field(None, description="Daftar penyakit kronis")
    current_medications: Optional[List[Dict[str, Any]]] = Field(
        None, description="Daftar obat yang sedang dikonsumsi"
    )
    emergency_contact_name: Optional[str] = Field(None, description="Nama kontak darurat utama")
    emergency_contact_phone: Optional[str] = Field(None, description="Nomor telepon kontak darurat")
    emergency_contact_relation: Optional[str] = Field(None, description="Hubungan dengan kontak darurat")
    bpjs_number: Optional[str] = Field(None, description="Nomor BPJS Kesehatan")
    insurance_provider: Optional[str] = Field(None, description="Penyedia asuransi")
    insurance_policy_number: Optional[str] = Field(None, description="Nomor polis asuransi")

    @field_validator("blood_type")
    @classmethod
    def validate_blood_type(cls, v: Optional[str]) -> Optional[str]:
        valid_types = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
        if v is not None and v not in valid_types:
            raise ValueError(f"Golongan darah tidak valid. Pilih salah satu: {', '.join(sorted(valid_types))}")
        return v


# ── Kontak Darurat ───────────────────────────────────────────────────────────


class EmergencyContactCreate(BaseModel):
    """Permintaan penambahan kontak darurat."""

    name: str = Field(..., min_length=2, max_length=255, description="Nama kontak")
    phone: str = Field(..., max_length=20, description="Nomor telepon kontak")
    relation: Optional[str] = Field(None, max_length=100, description="Hubungan (misal: Ibu, Ayah, Pasangan)")
    priority: int = Field(default=1, ge=1, le=5, description="Prioritas kontak (1-5)")
    can_view_health_status: bool = Field(default=False, description="Izinkan melihat status kesehatan")
    can_view_medications: bool = Field(default=False, description="Izinkan melihat daftar obat")
    can_view_consultation_history: bool = Field(default=False, description="Izinkan melihat riwayat konsultasi")


class EmergencyContactUpdate(BaseModel):
    """Permintaan pembaruan kontak darurat."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    relation: Optional[str] = Field(None, max_length=100)
    priority: Optional[int] = Field(None, ge=1, le=5)
    can_view_health_status: Optional[bool] = None
    can_view_medications: Optional[bool] = None
    can_view_consultation_history: Optional[bool] = None
    is_active: Optional[bool] = None


class EmergencyContactResponse(BaseModel):
    """Respons data kontak darurat."""

    id: UUID
    user_id: UUID
    name: str
    phone: str
    relation: Optional[str] = None
    priority: int
    can_view_health_status: bool
    can_view_medications: bool
    can_view_consultation_history: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── MedCard ──────────────────────────────────────────────────────────────────


class MedCardResponse(BaseModel):
    """Respons MedCard (kartu medis digital) — untuk pemilik."""

    user_id: UUID
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    current_medications: Optional[Any] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    bpjs_number: Optional[str] = None
    insurance_provider: Optional[str] = None
    qr_code_url: Optional[str] = None


class MedCardPublicResponse(BaseModel):
    """Respons MedCard publik — informasi darurat untuk penolong/paramedis."""

    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    pesan: str = Field(
        default="Informasi ini ditampilkan untuk keperluan darurat medis. "
        "Hubungi kontak darurat di atas jika diperlukan.",
        description="Pesan disclamer untuk publik",
    )

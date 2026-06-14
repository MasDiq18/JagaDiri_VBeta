"""
JagaDiri — Schema Rekam Medis & Tanda Vital
Schemas untuk health records, vaccination records, dan vital signs.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Health Record ────────────────────────────────────────────────────────────


class HealthRecordCreate(BaseModel):
    """Permintaan penambahan rekam medis."""

    record_type: str = Field(
        ..., description="Tipe rekam medis: lab_result, radiology, vaccination, surgery, "
        "hospitalization, screening, document, other",
    )
    title: str = Field(..., min_length=3, max_length=255, description="Judul rekam medis")
    date_of_record: date = Field(..., description="Tanggal pemeriksaan/tindakan")
    facility_name: Optional[str] = Field(None, max_length=255, description="Nama fasilitas kesehatan")
    doctor_name: Optional[str] = Field(None, max_length=255, description="Nama dokter")
    findings: Optional[str] = Field(None, description="Hasil pemeriksaan/temuan")
    file_urls: Optional[List[str]] = Field(None, description="URL file dokumen pendukung")
    is_shared_with_family: bool = Field(
        default=False, description="Bagikan dengan anggota keluarga"
    )
    tags: Optional[List[str]] = Field(None, description="Tag untuk kategorisasi")

    @field_validator("record_type")
    @classmethod
    def validate_record_type(cls, v: str) -> str:
        valid_types = {
            "lab_result", "radiology", "vaccination", "surgery",
            "hospitalization", "screening", "document", "other",
        }
        if v not in valid_types:
            raise ValueError(
                f"Tipe rekam medis tidak valid. Pilih: {', '.join(sorted(valid_types))}"
            )
        return v


class HealthRecordUpdate(BaseModel):
    """Permintaan pembaruan rekam medis."""

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    date_of_record: Optional[date] = None
    facility_name: Optional[str] = Field(None, max_length=255)
    doctor_name: Optional[str] = Field(None, max_length=255)
    findings: Optional[str] = None
    file_urls: Optional[List[str]] = None
    is_shared_with_family: Optional[bool] = None
    tags: Optional[List[str]] = None


class HealthRecordResponse(BaseModel):
    """Respons data rekam medis."""

    id: UUID
    user_id: UUID
    record_type: str
    title: str
    date_of_record: date
    facility_name: Optional[str] = None
    doctor_name: Optional[str] = None
    findings: Optional[str] = None
    file_urls: Optional[List[str]] = None
    is_shared_with_family: bool
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Vital Signs ──────────────────────────────────────────────────────────────


class VitalSignCreate(BaseModel):
    """Permintaan pencatatan tanda vital."""

    metric_type: str = Field(
        ..., description="Tipe metrik: blood_pressure, heart_rate, temperature, "
        "blood_sugar, spo2, weight, bmi",
    )
    value_numeric: Optional[float] = Field(
        None, description="Nilai numerik (untuk heart_rate, temperature, blood_sugar, spo2, weight, bmi)"
    )
    value_systolic: Optional[int] = Field(
        None, ge=50, le=300,
        description="Tekanan darah sistolik (mmHg)",
    )
    value_diastolic: Optional[int] = Field(
        None, ge=30, le=200,
        description="Tekanan darah diastolik (mmHg)",
    )
    value_text: Optional[str] = Field(None, max_length=255, description="Nilai teks tambahan")
    unit: Optional[str] = Field(None, max_length=30, description="Satuan pengukuran")
    source: Optional[str] = Field(
        None, max_length=50,
        description="Sumber data: manual, smartwatch, alat_ukur",
    )
    notes: Optional[str] = Field(None, description="Catatan tambahan")

    @field_validator("metric_type")
    @classmethod
    def validate_metric_type(cls, v: str) -> str:
        valid_types = {
            "blood_pressure", "heart_rate", "temperature",
            "blood_sugar", "spo2", "weight", "bmi",
        }
        if v not in valid_types:
            raise ValueError(
                f"Tipe metrik tidak valid. Pilih: {', '.join(sorted(valid_types))}"
            )
        return v


class VitalSignResponse(BaseModel):
    """Respons data tanda vital."""

    id: UUID
    user_id: UUID
    metric_type: str
    value_numeric: Optional[float] = None
    value_systolic: Optional[int] = None
    value_diastolic: Optional[int] = None
    value_text: Optional[str] = None
    unit: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

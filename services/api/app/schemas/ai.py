"""
JagaDiri — Schema AI & Symptom Checker
Schemas untuk analisis gejala dan wawasan kesehatan.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SymptomCheckRequest(BaseModel):
    """Permintaan pengecekan gejala."""

    gejala: List[str] = Field(
        ..., min_length=1, max_length=20,
        description="Daftar gejala yang dialami (dalam Bahasa Indonesia). "
        "Contoh: ['pusing', 'mual', 'demam']",
    )
    usia: Optional[int] = Field(None, ge=0, le=150, description="Usia pasien (tahun)")
    jenis_kelamin: Optional[str] = Field(
        None, description="Jenis kelamin: male, female"
    )
    durasi_hari: Optional[int] = Field(
        None, ge=1, le=365,
        description="Berapa hari gejala sudah berlangsung",
    )


class PossibleCondition(BaseModel):
    """Kondisi yang mungkin berdasarkan gejala."""

    nama_kondisi: str = Field(..., description="Nama kondisi/penyakit")
    nama_kondisi_medis: str = Field(..., description="Nama medis/ilmiah")
    kode_icd10: Optional[str] = Field(None, description="Kode ICD-10")
    probabilitas: str = Field(..., description="Tingkat kemungkinan: rendah, sedang, tinggi")
    penjelasan: str = Field(..., description="Penjelasan singkat tentang kondisi")
    saran_tindakan: str = Field(..., description="Saran tindakan yang direkomendasikan")


class SymptomCheckResponse(BaseModel):
    """Respons analisis gejala."""

    gejala_dianalisis: List[str] = Field(..., description="Gejala yang berhasil dianalisis")
    gejala_tidak_dikenal: List[str] = Field(
        default_factory=list,
        description="Gejala yang tidak dikenali sistem",
    )
    kondisi_mungkin: List[PossibleCondition] = Field(
        ..., description="Daftar kondisi yang mungkin"
    )
    tingkat_urgensi: str = Field(
        ..., description="Tingkat urgensi: rendah, sedang, tinggi, darurat"
    )
    saran_umum: str = Field(..., description="Saran umum berdasarkan gejala")
    disclaimer: str = Field(
        default="⚠️ PENTING: Hasil analisis ini bukan diagnosis medis. "
        "Analisis ini dibuat oleh sistem berbasis aturan dan BUKAN pengganti "
        "konsultasi dengan dokter. Segera kunjungi fasilitas kesehatan terdekat "
        "jika kondisi Anda memburuk atau terasa mengkhawatirkan. "
        "Jangan menunda penanganan medis berdasarkan hasil ini.",
        description="Pesan disclaimer medis",
    )


class HealthInsightResponse(BaseModel):
    """Respons wawasan kesehatan."""

    user_id: UUID
    ringkasan_kesehatan: str = Field(..., description="Ringkasan kondisi kesehatan")
    saran_kesehatan: List[str] = Field(..., description="Daftar saran kesehatan")
    pengingat: List[str] = Field(
        default_factory=list, description="Pengingat jadwal kesehatan"
    )
    skor_kesehatan: Optional[int] = Field(
        None, ge=0, le=100, description="Skor kesehatan keseluruhan (0-100)"
    )
    disclaimer: str = Field(
        default="Wawasan ini dihasilkan berdasarkan data yang Anda masukkan "
        "dan bukan merupakan nasihat medis profesional.",
    )

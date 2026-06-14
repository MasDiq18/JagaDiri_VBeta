"""
JagaDiri — Router Dokter & Konsultasi
Endpoints untuk pencarian dokter, booking konsultasi, SOAP notes, dan rating.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.consultation import (
    DoctorResponse,
    DoctorListFilter,
    ConsultationCreate,
    ConsultationResponse,
    ConsultationStatusUpdate,
    ConsultationNoteCreate,
    ConsultationNoteResponse,
    RateRequest,
)
from app.services import consultation_service

router = APIRouter(prefix="/consultations", tags=["Konsultasi Dokter"])


@router.get(
    "/doctors",
    status_code=status.HTTP_200_OK,
    summary="Ambil daftar dokter terverifikasi",
)
async def read_doctors(
    specialization: Optional[str] = None,
    is_online: Optional[bool] = None,
    available_for_home_visit: Optional[bool] = None,
    min_rating: Optional[float] = None,
    max_fee: Optional[int] = None,
    search: Optional[str] = None,
    halaman: int = 1,
    per_halaman: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Mencari dan memfilter daftar dokter terverifikasi di Indonesia."""
    filters = DoctorListFilter(
        specialization=specialization,
        is_online=is_online,
        available_for_home_visit=available_for_home_visit,
        min_rating=min_rating,
        max_fee=max_fee,
        search=search,
        halaman=halaman,
        per_halaman=per_halaman,
    )
    doctors, total = await consultation_service.list_doctors(db, filters)
    return {
        "doctors": [consultation_service.format_doctor_response(d) for d in doctors],
        "total": total,
        "halaman": halaman,
        "per_halaman": per_halaman,
    }


@router.get(
    "/doctors/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil detail dokter",
)
async def read_doctor(doctor_id: UUID, db: AsyncSession = Depends(get_db)):
    """Mengambil detail profil lengkap dan jadwal praktik dokter tertentu."""
    doctor = await consultation_service.get_doctor(db, doctor_id)
    return consultation_service.format_doctor_response(doctor)


@router.post(
    "/booking",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Pesan jadwal konsultasi baru",
)
async def booking(
    data: ConsultationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memesan jadwal konsultasi dokter baru (chat, video, kunjungan rumah)."""
    consultation = await consultation_service.create_consultation(db, current_user.id, data)
    return consultation_service.format_consultation_response(consultation)


@router.get(
    "/history",
    response_model=List[ConsultationResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil riwayat konsultasi",
)
async def read_history(
    status_filter: Optional[str] = None,
    role: str = "patient",
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil daftar riwayat konsultasi medis yang telah dipesan pengguna (atau dokter)."""
    consultations = await consultation_service.list_consultations(
        db, current_user.id, role, status_filter, limit, offset
    )
    return [consultation_service.format_consultation_response(c) for c in consultations]


@router.get(
    "/history/{consultation_id}",
    response_model=ConsultationResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil detail riwayat konsultasi",
)
async def read_consultation(
    consultation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil informasi detail untuk satu konsultasi medis spesifik."""
    consultation = await consultation_service.get_consultation(db, consultation_id, current_user.id)
    return consultation_service.format_consultation_response(consultation)


@router.put(
    "/history/{consultation_id}/status",
    response_model=ConsultationResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui status konsultasi",
)
async def update_status(
    consultation_id: UUID,
    data: ConsultationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memperbarui status konsultasi (misal: membatalkan, menandakan sedang berjalan, atau selesai)."""
    consultation = await consultation_service.update_consultation_status(
        db, consultation_id, current_user.id, data
    )
    return consultation_service.format_consultation_response(consultation)


@router.post(
    "/history/{consultation_id}/note",
    response_model=ConsultationNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat catatan rekam medis SOAP (Dokter)",
)
async def create_note(
    consultation_id: UUID,
    data: ConsultationNoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Menambahkan catatan SOAP rekam medis (Subjective, Objective, Assessment, Plan) oleh dokter."""
    return await consultation_service.create_consultation_note(
        db, consultation_id, current_user.id, data
    )


@router.post(
    "/history/{consultation_id}/rate",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
    summary="Beri rating konsultasi",
)
async def rate(
    consultation_id: UUID,
    data: RateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memberikan penilaian rating (1-5 bintang) dan review setelah konsultasi selesai."""
    doctor = await consultation_service.rate_consultation(db, consultation_id, current_user.id, data)
    return consultation_service.format_doctor_response(doctor)

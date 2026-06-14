"""
JagaDiri — Router Rekam Medis & Tanda Vital
Endpoints untuk dokumen rekam medis mandiri dan pemantauan tanda vital.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.health_record import (
    HealthRecordResponse,
    HealthRecordCreate,
    HealthRecordUpdate,
    VitalSignResponse,
    VitalSignCreate,
)
from app.services import health_record_service

router = APIRouter(prefix="/health-records", tags=["Rekam Medis & Tanda Vital"])


# === Vitals routes HARUS di atas /{record_id} untuk menghindari path conflict ===

@router.post(
    "/vitals",
    response_model=VitalSignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Catat tanda vital baru",
)
async def create_vital(
    data: VitalSignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mencatat data tanda vital baru seperti tekanan darah, detak jantung, suhu tubuh, atau berat badan."""
    return await health_record_service.create_vital_sign(db, current_user.id, data)


@router.get(
    "/vitals",
    response_model=List[VitalSignResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil riwayat tanda vital",
)
async def read_vitals(
    metric_type: Optional[str] = Query(None, description="Filter berdasarkan tipe metrik tanda vital"),
    limit: int = Query(100, ge=1, le=500, description="Maksimum jumlah data yang diambil"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil riwayat pencatatan tanda vital pengguna (berguna untuk grafik tren)."""
    return await health_record_service.list_vital_signs(db, current_user.id, metric_type, limit)


# === Health Records CRUD ===

@router.post(
    "",
    response_model=HealthRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah dokumen rekam medis",
)
async def create_record(
    data: HealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Menambahkan riwayat rekam medis mandiri baru (seperti hasil laboratorium, foto rontgen, dll)."""
    return await health_record_service.create_health_record(db, current_user.id, data)


@router.get(
    "",
    response_model=List[HealthRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil daftar rekam medis",
)
async def read_records(
    record_type: Optional[str] = Query(None, description="Filter berdasarkan tipe rekam medis"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil seluruh daftar dokumen rekam medis milik pengguna."""
    return await health_record_service.list_health_records(db, current_user.id, record_type)


@router.get(
    "/{record_id}",
    response_model=HealthRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil detail rekam medis",
)
async def read_record(
    record_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil detail satu rekam medis tertentu beserta lampiran file dokumen."""
    return await health_record_service.get_health_record(db, current_user.id, record_id)


@router.put(
    "/{record_id}",
    response_model=HealthRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui rekam medis",
)
async def update_record(
    record_id: UUID,
    data: HealthRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memperbarui informasi deskriptif rekam medis."""
    return await health_record_service.update_health_record(db, current_user.id, record_id, data)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_200_OK,
    summary="Hapus rekam medis",
)
async def delete_record(
    record_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Menghapus dokumen rekam medis secara permanen."""
    await health_record_service.delete_health_record(db, current_user.id, record_id)
    return {"pesan": "Rekam medis berhasil dihapus"}

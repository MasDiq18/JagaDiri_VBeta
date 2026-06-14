"""
JagaDiri — Router SafePing & SOS
Endpoints untuk SafePing check-in, konfigurasi, dan penanganan SOS darurat.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.safeping import (
    SafePingConfigResponse,
    SafePingConfigUpdate,
    CheckInRequest,
    CheckInResponse,
    CheckInHistoryResponse,
    SOSRequest,
    SOSResponse,
    SOSResolveRequest,
)
from app.services import safeping_service

router = APIRouter(prefix="/safeping", tags=["SafeGuard & SOS"])


@router.get(
    "/config",
    response_model=SafePingConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil konfigurasi SafePing",
)
async def read_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil konfigurasi SafePing (waktu check-in harian, opsi eskalasi) milik pengguna."""
    return await safeping_service.get_safeping_config(db, current_user.id)


@router.put(
    "/config",
    response_model=SafePingConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui konfigurasi SafePing",
)
async def update_config(
    data: SafePingConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memperbarui pengaturan check-in harian SafePing."""
    return await safeping_service.update_safeping_config(db, current_user.id, data)


@router.post(
    "/checkin",
    response_model=CheckInResponse,
    status_code=status.HTTP_200_OK,
    summary="Lakukan check-in harian",
)
async def checkin(
    data: CheckInRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengirim respons check-in harian yang menyatakan pengguna dalam kondisi aman."""
    return await safeping_service.process_checkin(db, current_user.id, data)


@router.get(
    "/checkin/history",
    response_model=List[CheckInHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil riwayat check-in",
)
async def read_checkin_history(
    limit: int = 30,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil daftar riwayat check-in pengguna dalam rentang waktu tertentu."""
    return await safeping_service.get_checkin_history(db, current_user.id, limit, offset)


@router.post(
    "/sos",
    response_model=SOSResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Aktifkan SOS darurat",
)
async def trigger_sos(
    data: SOSRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mengaktifkan sinyal SOS darurat secara instan.
    Sistem akan mengirimkan SMS/pesan notifikasi beserta peta lokasi ke seluruh kontak darurat aktif,
    dan eskalasi ke 119 jika diaktifkan.
    """
    return await safeping_service.trigger_sos(db, current_user.id, data)


@router.post(
    "/sos/{sos_id}/resolve",
    response_model=SOSResponse,
    status_code=status.HTTP_200_OK,
    summary="Selesaikan kejadian SOS",
)
async def resolve_sos(
    sos_id: UUID,
    data: SOSResolveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Menyelesaikan status SOS aktif (misalnya menjadi aman atau alarm palsu)."""
    return await safeping_service.resolve_sos(db, current_user.id, sos_id, data)


@router.get(
    "/sos/history",
    response_model=List[SOSResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil riwayat SOS darurat",
)
async def read_sos_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil daftar riwayat aktivasi SOS darurat pengguna."""
    return await safeping_service.get_sos_history(db, current_user.id, limit, offset)

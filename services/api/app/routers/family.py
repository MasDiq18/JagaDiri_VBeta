"""
JagaDiri — Router Portal Keluarga
Endpoints untuk mengelola koneksi keluarga, berbagi data kesehatan, dan pemantauan dari jarak jauh.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.family import (
    FamilyConnectionResponse,
    FamilyInviteRequest,
    FamilyPermissionUpdate,
    FamilyMemberStatusResponse,
)
from app.services import family_service

router = APIRouter(prefix="/family", tags=["Portal Keluarga"])


@router.post(
    "/invite",
    response_model=FamilyConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Undang anggota keluarga",
)
async def invite(
    data: FamilyInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengirim undangan koneksi keluarga/caregiver berdasarkan alamat email."""
    return await family_service.send_invite(db, current_user.id, data)


@router.get(
    "/connections",
    response_model=List[FamilyConnectionResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil daftar koneksi keluarga",
)
async def read_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil daftar seluruh koneksi keluarga yang terhubung dengan akun pengguna."""
    return await family_service.list_connections(db, current_user.id)


@router.post(
    "/connections/{connection_id}/accept",
    response_model=FamilyConnectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Terima undangan keluarga",
)
async def accept(
    connection_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Menerima undangan koneksi keluarga yang masuk."""
    return await family_service.accept_invite(db, current_user.id, connection_id)


@router.put(
    "/connections/{connection_id}/permissions",
    response_model=FamilyConnectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui izin berbagi data",
)
async def update_perms(
    connection_id: UUID,
    data: FamilyPermissionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memperbarui tingkat izin pembagian informasi medis (seperti vitals, medReminder, dll) ke keluarga."""
    return await family_service.update_permissions(db, current_user.id, connection_id, data)


@router.get(
    "/member/{patient_id}/status",
    response_model=FamilyMemberStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil status kesehatan anggota keluarga (untuk caregiver)",
)
async def read_member_status(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil status pemantauan kesehatan terkini dari anggota keluarga yang diikuti (hanya jika diizinkan)."""
    return await family_service.get_member_status(db, current_user.id, patient_id)

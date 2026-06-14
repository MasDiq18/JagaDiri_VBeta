"""
JagaDiri — Router Pengguna & Profil
Endpoints untuk profil pengguna, profil medis, kontak darurat, dan MedCard.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserProfileUpdate,
    MedicalProfileResponse,
    MedicalProfileUpdate,
    EmergencyContactResponse,
    EmergencyContactCreate,
    EmergencyContactUpdate,
    MedCardResponse,
    MedCardPublicResponse,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Pengguna & Profil"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil profil pengguna saat ini",
)
async def read_me(current_user: User = Depends(get_current_user)):
    """Mengambil data profil lengkap milik pengguna yang sedang login."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui profil pengguna saat ini",
)
async def update_me(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memperbarui informasi profil pribadi pengguna."""
    return await user_service.update_user_profile(db, current_user.id, data)


@router.get(
    "/me/medical",
    response_model=MedicalProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil profil medis pengguna",
)
async def read_medical(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil riwayat medis dasar, golongan darah, alergi, dan info asuransi pengguna."""
    return await user_service.get_medical_profile(db, current_user.id)


@router.put(
    "/me/medical",
    response_model=MedicalProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui profil medis pengguna",
)
async def update_medical(
    data: MedicalProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memperbarui informasi rekam medis mandiri (alergi, riwayat penyakit kronis, dll)."""
    return await user_service.update_medical_profile(db, current_user.id, data)


@router.get(
    "/me/contacts",
    response_model=List[EmergencyContactResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil daftar kontak darurat",
)
async def read_contacts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil seluruh daftar kontak darurat (maksimal 5) yang dikonfigurasi pengguna."""
    return await user_service.list_emergency_contacts(db, current_user.id)


@router.post(
    "/me/contacts",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah kontak darurat baru",
)
async def create_contact(
    data: EmergencyContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Menambahkan satu kontak darurat baru (keluarga/teman dekat)."""
    return await user_service.create_emergency_contact(db, current_user.id, data)


@router.put(
    "/me/contacts/{contact_id}",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui kontak darurat",
)
async def update_contact(
    contact_id: UUID,
    data: EmergencyContactUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memperbarui detail atau hak akses dari kontak darurat tertentu."""
    return await user_service.update_emergency_contact(db, current_user.id, contact_id, data)


@router.delete(
    "/me/contacts/{contact_id}",
    status_code=status.HTTP_200_OK,
    summary="Hapus kontak darurat",
)
async def delete_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Menghapus (soft delete) salah satu kontak darurat."""
    await user_service.delete_emergency_contact(db, current_user.id, contact_id)
    return {"pesan": "Kontak darurat berhasil dihapus"}


@router.get(
    "/me/medcard",
    response_model=MedCardResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil kartu MedCard digital",
)
async def read_medcard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil data MedCard digital yang berisi ringkasan info penyelamatan darurat dan QR Code."""
    return await user_service.get_medcard(db, current_user.id)


@router.get(
    "/medcard/{user_id}/public",
    response_model=MedCardPublicResponse,
    status_code=status.HTTP_200_OK,
    summary="Akses publik MedCard darurat",
)
async def read_medcard_public(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Akses publik tanpa login untuk menampilkan info penyelamatan medis krusial.
    Hanya ditujukan untuk petugas medis atau penolong yang memindai QR Code di layar kunci/gelang darurat pengguna.
    """
    return await user_service.get_medcard_public(db, user_id)

"""
JagaDiri — Layanan Pengguna & Profil
Business logic untuk profil, profil medis, kontak darurat, dan MedCard.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import EmergencyContact, User, UserMedicalProfile
from app.schemas.user import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    MedCardPublicResponse,
    MedCardResponse,
    MedicalProfileUpdate,
    UserProfileUpdate,
)

logger = logging.getLogger("jagadiri.user")


# ── Profil Pengguna ──────────────────────────────────────────────────────────


async def get_user_profile(db: AsyncSession, user_id: UUID) -> User:
    """Ambil profil pengguna."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan.",
        )
    return user


async def update_user_profile(
    db: AsyncSession, user_id: UUID, data: UserProfileUpdate
) -> User:
    """Perbarui profil pengguna."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan.",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    logger.info("Profil diperbarui: user_id=%s", user_id)
    return user


# ── Profil Medis ─────────────────────────────────────────────────────────────


async def get_medical_profile(db: AsyncSession, user_id: UUID) -> UserMedicalProfile:
    """Ambil profil medis pengguna."""
    result = await db.execute(
        select(UserMedicalProfile).where(UserMedicalProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        # Buat profil medis kosong jika belum ada
        profile = UserMedicalProfile(user_id=user_id)
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
    return profile


async def update_medical_profile(
    db: AsyncSession, user_id: UUID, data: MedicalProfileUpdate
) -> UserMedicalProfile:
    """Perbarui profil medis pengguna."""
    result = await db.execute(
        select(UserMedicalProfile).where(UserMedicalProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserMedicalProfile(user_id=user_id)
        db.add(profile)
        await db.flush()

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.flush()
    await db.refresh(profile)
    logger.info("Profil medis diperbarui: user_id=%s", user_id)
    return profile


# ── Kontak Darurat ───────────────────────────────────────────────────────────


async def list_emergency_contacts(
    db: AsyncSession, user_id: UUID
) -> List[EmergencyContact]:
    """Ambil daftar kontak darurat."""
    result = await db.execute(
        select(EmergencyContact)
        .where(EmergencyContact.user_id == user_id)
        .order_by(EmergencyContact.priority)
    )
    return list(result.scalars().all())


async def create_emergency_contact(
    db: AsyncSession, user_id: UUID, data: EmergencyContactCreate
) -> EmergencyContact:
    """Tambah kontak darurat baru."""
    # Cek jumlah kontak (maksimum 5)
    result = await db.execute(
        select(func.count()).select_from(EmergencyContact).where(
            EmergencyContact.user_id == user_id,
            EmergencyContact.is_active == True,  # noqa: E712
        )
    )
    count = result.scalar()
    if count and count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maksimum 5 kontak darurat. Hapus salah satu sebelum menambah yang baru.",
        )

    contact = EmergencyContact(
        user_id=user_id,
        **data.model_dump(),
    )
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    logger.info("Kontak darurat ditambahkan: user_id=%s, contact=%s", user_id, contact.name)
    return contact


async def update_emergency_contact(
    db: AsyncSession, user_id: UUID, contact_id: UUID, data: EmergencyContactUpdate
) -> EmergencyContact:
    """Perbarui kontak darurat."""
    result = await db.execute(
        select(EmergencyContact).where(
            EmergencyContact.id == contact_id,
            EmergencyContact.user_id == user_id,
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kontak darurat tidak ditemukan.",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    await db.flush()
    await db.refresh(contact)
    return contact


async def delete_emergency_contact(
    db: AsyncSession, user_id: UUID, contact_id: UUID
) -> None:
    """Hapus kontak darurat (soft delete)."""
    result = await db.execute(
        select(EmergencyContact).where(
            EmergencyContact.id == contact_id,
            EmergencyContact.user_id == user_id,
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kontak darurat tidak ditemukan.",
        )

    contact.is_active = False
    await db.flush()
    logger.info("Kontak darurat dihapus: user_id=%s, contact_id=%s", user_id, contact_id)


# ── MedCard ──────────────────────────────────────────────────────────────────


async def get_medcard(db: AsyncSession, user_id: UUID) -> MedCardResponse:
    """Ambil MedCard pengguna (untuk pemilik)."""
    user = await get_user_profile(db, user_id)

    result = await db.execute(
        select(UserMedicalProfile).where(UserMedicalProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    # Generate URL QR code (mock — di produksi gunakan library qrcode)
    qr_url = f"https://api.jagadiri.id/v1/users/medcard/{user_id}/public"

    return MedCardResponse(
        user_id=user.id,
        full_name=user.full_name,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        blood_type=profile.blood_type if profile else None,
        allergies=profile.allergies if profile else None,
        chronic_conditions=profile.chronic_conditions if profile else None,
        current_medications=profile.current_medications if profile else None,
        emergency_contact_name=profile.emergency_contact_name if profile else None,
        emergency_contact_phone=profile.emergency_contact_phone if profile else None,
        emergency_contact_relation=profile.emergency_contact_relation if profile else None,
        bpjs_number=profile.bpjs_number if profile else None,
        insurance_provider=profile.insurance_provider if profile else None,
        qr_code_url=qr_url,
    )


async def get_medcard_public(db: AsyncSession, user_id: UUID) -> MedCardPublicResponse:
    """Ambil MedCard publik (untuk paramedis/penolong — tanpa autentikasi)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data tidak ditemukan.",
        )

    profile_result = await db.execute(
        select(UserMedicalProfile).where(UserMedicalProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    return MedCardPublicResponse(
        full_name=user.full_name,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        blood_type=profile.blood_type if profile else None,
        allergies=profile.allergies if profile else None,
        chronic_conditions=profile.chronic_conditions if profile else None,
        emergency_contact_name=profile.emergency_contact_name if profile else None,
        emergency_contact_phone=profile.emergency_contact_phone if profile else None,
        emergency_contact_relation=profile.emergency_contact_relation if profile else None,
    )

"""
JagaDiri — Router Pengingat Obat & Kepatuhan
Endpoints untuk pengelolaan jadwal minum obat, pencatatan konsumsi obat, dan laporan kepatuhan.
"""

from datetime import date
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.medication import (
    MedicationReminderResponse,
    MedicationReminderCreate,
    MedicationReminderUpdate,
    MedicationTakenRequest,
    AdherenceLogResponse,
    AdherenceReportResponse,
)
from app.services import medication_service

router = APIRouter(prefix="/medications", tags=["Manajemen Obat (MedReminder)"])


@router.get(
    "/reminders",
    response_model=List[MedicationReminderResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil daftar pengingat obat",
)
async def read_reminders(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil seluruh daftar pengingat obat milik pengguna."""
    return await medication_service.list_reminders(db, current_user.id, active_only)


@router.get(
    "/reminders/today",
    response_model=List[MedicationReminderResponse],
    status_code=status.HTTP_200_OK,
    summary="Ambil jadwal obat hari ini",
)
async def read_today_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil jadwal pengingat obat yang harus dikonsumsi pengguna hari ini."""
    return await medication_service.get_today_reminders(db, current_user.id)


@router.post(
    "/reminders",
    response_model=MedicationReminderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat pengingat obat baru",
)
async def create_reminder(
    data: MedicationReminderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Menambahkan pengingat obat baru lengkap dengan nama obat, dosis, frekuensi, dan waktu alarm."""
    return await medication_service.create_reminder(db, current_user.id, data)


@router.get(
    "/reminders/{reminder_id}",
    response_model=MedicationReminderResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil detail pengingat obat",
)
async def read_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mengambil informasi detail untuk satu pengingat obat spesifik."""
    return await medication_service.get_reminder(db, current_user.id, reminder_id)


@router.put(
    "/reminders/{reminder_id}",
    response_model=MedicationReminderResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui pengingat obat",
)
async def update_reminder(
    reminder_id: UUID,
    data: MedicationReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Memperbarui jadwal, dosis, atau status aktif dari pengingat obat tertentu."""
    return await medication_service.update_reminder(db, current_user.id, reminder_id, data)


@router.delete(
    "/reminders/{reminder_id}",
    status_code=status.HTTP_200_OK,
    summary="Nonaktifkan pengingat obat",
)
async def delete_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Menonaktifkan (soft delete) pengingat obat."""
    await medication_service.delete_reminder(db, current_user.id, reminder_id)
    return {"pesan": "Pengingat obat berhasil dinonaktifkan"}


@router.post(
    "/reminders/{reminder_id}/take",
    response_model=AdherenceLogResponse,
    status_code=status.HTTP_200_OK,
    summary="Catat konsumsi obat",
)
async def mark_taken(
    reminder_id: UUID,
    data: MedicationTakenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mencatat konsumsi obat ke log kepatuhan (adherence log).
    Dapat disertai dengan catatan tambahan dan tautan foto bukti konsumsi obat.
    """
    return await medication_service.mark_taken(db, current_user.id, reminder_id, data)


@router.get(
    "/report",
    response_model=AdherenceReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil laporan kepatuhan minum obat",
)
async def read_report(
    start_date: Optional[date] = Query(None, description="Tanggal awal periode laporan"),
    end_date: Optional[date] = Query(None, description="Tanggal akhir periode laporan"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mengambil kalkulasi persentase kepatuhan minum obat pengguna untuk periode waktu tertentu.
    Juga mengembalikan rincian per obat yang terjadwal.
    """
    return await medication_service.get_adherence_report(db, current_user.id, start_date, end_date)

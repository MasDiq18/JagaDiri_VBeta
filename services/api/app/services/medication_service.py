"""
JagaDiri — Layanan Pengingat Obat & Kepatuhan
Business logic untuk medication reminders, adherence tracking, dan laporan.
"""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.medication import MedicationAdherenceLog, MedicationReminder
from app.schemas.medication import (
    AdherencePerMedication,
    AdherenceReportResponse,
    MedicationReminderCreate,
    MedicationReminderUpdate,
    MedicationTakenRequest,
)

logger = logging.getLogger("jagadiri.medication")


# ── Medication Reminders ─────────────────────────────────────────────────────


async def create_reminder(
    db: AsyncSession, user_id: UUID, data: MedicationReminderCreate
) -> MedicationReminder:
    """Buat pengingat obat baru."""

    reminder = MedicationReminder(
        user_id=user_id,
        medication_name=data.medication_name,
        dosage=data.dosage,
        times_per_day=data.times_per_day,
        reminder_times=data.reminder_times,
        with_food=data.with_food,
        start_date=data.start_date,
        end_date=data.end_date,
        notes=data.notes,
    )
    db.add(reminder)
    await db.flush()
    await db.refresh(reminder)

    logger.info(
        "Pengingat obat dibuat: user=%s, obat=%s", user_id, data.medication_name
    )
    return reminder


async def list_reminders(
    db: AsyncSession, user_id: UUID, active_only: bool = True
) -> List[MedicationReminder]:
    """Ambil daftar pengingat obat."""
    query = select(MedicationReminder).where(
        MedicationReminder.user_id == user_id
    )
    if active_only:
        query = query.where(MedicationReminder.is_active == True)  # noqa: E712

    query = query.order_by(MedicationReminder.medication_name)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_reminder(
    db: AsyncSession, user_id: UUID, reminder_id: UUID
) -> MedicationReminder:
    """Ambil detail pengingat obat."""
    result = await db.execute(
        select(MedicationReminder).where(
            and_(
                MedicationReminder.id == reminder_id,
                MedicationReminder.user_id == user_id,
            )
        )
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengingat obat tidak ditemukan.",
        )
    return reminder


async def update_reminder(
    db: AsyncSession, user_id: UUID, reminder_id: UUID, data: MedicationReminderUpdate
) -> MedicationReminder:
    """Perbarui pengingat obat."""
    reminder = await get_reminder(db, user_id, reminder_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)

    await db.flush()
    await db.refresh(reminder)
    logger.info("Pengingat obat diperbarui: id=%s", reminder_id)
    return reminder


async def delete_reminder(
    db: AsyncSession, user_id: UUID, reminder_id: UUID
) -> None:
    """Nonaktifkan pengingat obat."""
    reminder = await get_reminder(db, user_id, reminder_id)
    reminder.is_active = False
    await db.flush()
    logger.info("Pengingat obat dinonaktifkan: id=%s", reminder_id)


async def get_today_reminders(
    db: AsyncSession, user_id: UUID
) -> List[MedicationReminder]:
    """Ambil pengingat obat untuk hari ini."""
    today = date.today()
    result = await db.execute(
        select(MedicationReminder).where(
            and_(
                MedicationReminder.user_id == user_id,
                MedicationReminder.is_active == True,  # noqa: E712
                MedicationReminder.start_date <= today,
                (MedicationReminder.end_date >= today) | (MedicationReminder.end_date.is_(None)),
            )
        ).order_by(MedicationReminder.medication_name)
    )
    return list(result.scalars().all())


# ── Adherence Logging ────────────────────────────────────────────────────────


async def mark_taken(
    db: AsyncSession,
    user_id: UUID,
    reminder_id: UUID,
    data: MedicationTakenRequest,
) -> MedicationAdherenceLog:
    """Tandai obat sudah diminum."""
    reminder = await get_reminder(db, user_id, reminder_id)
    now = datetime.now(timezone.utc)

    # Buat log kepatuhan
    log = MedicationAdherenceLog(
        reminder_id=reminder_id,
        user_id=user_id,
        scheduled_at=now,
        taken_at=now,
        status="taken",
        notes=data.notes,
        photo_proof_url=data.photo_proof_url,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)

    logger.info(
        "Obat diminum: user=%s, reminder=%s, obat=%s",
        user_id, reminder_id, reminder.medication_name,
    )
    return log


# ── Laporan Kepatuhan ────────────────────────────────────────────────────────


async def get_adherence_report(
    db: AsyncSession,
    user_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> AdherenceReportResponse:
    """Hitung laporan kepatuhan minum obat."""

    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    # Ambil semua log dalam periode
    result = await db.execute(
        select(MedicationAdherenceLog).where(
            and_(
                MedicationAdherenceLog.user_id == user_id,
                MedicationAdherenceLog.scheduled_at >= start_dt,
                MedicationAdherenceLog.scheduled_at <= end_dt,
            )
        )
    )
    logs = result.scalars().all()

    total = len(logs)
    taken = sum(1 for log in logs if log.status == "taken")
    skipped = sum(1 for log in logs if log.status == "skipped")
    late = sum(1 for log in logs if log.status == "late")
    pct = (taken / total * 100) if total > 0 else 0.0

    # Detail per obat
    reminders_result = await db.execute(
        select(MedicationReminder).where(MedicationReminder.user_id == user_id)
    )
    reminders = reminders_result.scalars().all()

    per_medication = []
    for rem in reminders:
        rem_logs = [log for log in logs if log.reminder_id == rem.id]
        rem_total = len(rem_logs)
        rem_taken = sum(1 for l in rem_logs if l.status == "taken")
        rem_pct = (rem_taken / rem_total * 100) if rem_total > 0 else 0.0

        per_medication.append(
            AdherencePerMedication(
                reminder_id=rem.id,
                medication_name=rem.medication_name,
                total_jadwal=rem_total,
                total_diminum=rem_taken,
                persentase=round(rem_pct, 1),
            )
        )

    return AdherenceReportResponse(
        user_id=user_id,
        periode_awal=start_date,
        periode_akhir=end_date,
        total_jadwal=total,
        total_diminum=taken,
        total_dilewati=skipped,
        total_terlambat=late,
        persentase_kepatuhan=round(pct, 1),
        detail_per_obat=per_medication,
    )

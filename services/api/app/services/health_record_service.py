"""
JagaDiri — Layanan Rekam Medis & Tanda Vital
Business logic untuk rekam medis mandiri dan pemantauan tanda vital.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_record import HealthRecord, VitalSign
from app.schemas.health_record import HealthRecordCreate, HealthRecordUpdate, VitalSignCreate

logger = logging.getLogger("jagadiri.health_record")


async def create_health_record(
    db: AsyncSession, user_id: UUID, data: HealthRecordCreate
) -> HealthRecord:
    """Tambahkan rekam medis baru."""
    record = HealthRecord(
        user_id=user_id,
        record_type=data.record_type,
        title=data.title,
        date_of_record=data.date_of_record,
        facility_name=data.facility_name,
        doctor_name=data.doctor_name,
        findings=data.findings,
        file_urls=data.file_urls,
        is_shared_with_family=data.is_shared_with_family,
        tags=data.tags,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    logger.info("Rekam medis ditambahkan: user=%s, title=%s", user_id, data.title)
    return record


async def list_health_records(
    db: AsyncSession, user_id: UUID, record_type: Optional[str] = None
) -> List[HealthRecord]:
    """Ambil daftar rekam medis pengguna."""
    query = select(HealthRecord).where(HealthRecord.user_id == user_id)
    if record_type:
        query = query.where(HealthRecord.record_type == record_type)

    query = query.order_by(desc(HealthRecord.date_of_record))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_health_record(
    db: AsyncSession, user_id: UUID, record_id: UUID
) -> HealthRecord:
    """Ambil satu detail rekam medis."""
    result = await db.execute(
        select(HealthRecord).where(
            and_(
                HealthRecord.id == record_id,
                HealthRecord.user_id == user_id,
            )
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rekam medis tidak ditemukan.",
        )
    return record


async def update_health_record(
    db: AsyncSession, user_id: UUID, record_id: UUID, data: HealthRecordUpdate
) -> HealthRecord:
    """Perbarui dokumen rekam medis."""
    record = await get_health_record(db, user_id, record_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    await db.flush()
    await db.refresh(record)
    logger.info("Rekam medis diperbarui: id=%s", record_id)
    return record


async def delete_health_record(
    db: AsyncSession, user_id: UUID, record_id: UUID
) -> None:
    """Hapus rekam medis (hard delete untuk dokumen medis mandiri)."""
    record = await get_health_record(db, user_id, record_id)
    await db.delete(record)
    await db.flush()
    logger.info("Rekam medis dihapus: id=%s", record_id)


async def create_vital_sign(
    db: AsyncSession, user_id: UUID, data: VitalSignCreate
) -> VitalSign:
    """Catat tanda vital baru."""
    vital = VitalSign(
        user_id=user_id,
        metric_type=data.metric_type,
        value_numeric=data.value_numeric,
        value_systolic=data.value_systolic,
        value_diastolic=data.value_diastolic,
        value_text=data.value_text,
        unit=data.unit,
        source=data.source,
        notes=data.notes,
    )
    db.add(vital)
    await db.flush()
    await db.refresh(vital)
    logger.info("Tanda vital dicatat: user=%s, metrik=%s", user_id, data.metric_type)
    return vital


async def list_vital_signs(
    db: AsyncSession, user_id: UUID, metric_type: Optional[str] = None, limit: int = 100
) -> List[VitalSign]:
    """Ambil daftar riwayat tanda vital."""
    query = select(VitalSign).where(VitalSign.user_id == user_id)
    if metric_type:
        query = query.where(VitalSign.metric_type == metric_type)

    query = query.order_by(desc(VitalSign.created_at)).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())

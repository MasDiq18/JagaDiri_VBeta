"""
JagaDiri — Layanan SafePing & SOS
Business logic untuk check-in harian, konfigurasi SafePing, eskalasi, dan SOS darurat.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.safeping import SafePingConfig, SafePingLog, SOSEvent
from app.models.user import EmergencyContact
from app.schemas.safeping import (
    CheckInRequest,
    SafePingConfigUpdate,
    SOSRequest,
    SOSResolveRequest,
)
from app.services.notification_service import notification_service

logger = logging.getLogger("jagadiri.safeping")


# ── SafePing Config ──────────────────────────────────────────────────────────


async def get_safeping_config(db: AsyncSession, user_id: UUID) -> SafePingConfig:
    """Ambil konfigurasi SafePing pengguna."""
    result = await db.execute(
        select(SafePingConfig).where(SafePingConfig.user_id == user_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        # Buat default jika belum ada
        config = SafePingConfig(user_id=user_id)
        db.add(config)
        await db.flush()
        await db.refresh(config)
    return config


async def update_safeping_config(
    db: AsyncSession, user_id: UUID, data: SafePingConfigUpdate
) -> SafePingConfig:
    """Perbarui konfigurasi SafePing."""
    config = await get_safeping_config(db, user_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    await db.flush()
    await db.refresh(config)
    logger.info("SafePing config diperbarui: user_id=%s", user_id)
    return config


# ── Check-In ─────────────────────────────────────────────────────────────────


async def process_checkin(
    db: AsyncSession, user_id: UUID, data: CheckInRequest
) -> SafePingLog:
    """Proses check-in harian SafePing."""

    now = datetime.now(timezone.utc)

    # Cek apakah ada pending check-in hari ini
    result = await db.execute(
        select(SafePingLog).where(
            and_(
                SafePingLog.user_id == user_id,
                SafePingLog.status == "pending",
            )
        ).order_by(desc(SafePingLog.scheduled_at)).limit(1)
    )
    pending_log = result.scalar_one_or_none()

    if pending_log:
        # Respons pada check-in yang tertunda
        pending_log.responded_at = now
        pending_log.status = "responded"
        pending_log.mood_score = data.mood_score
        pending_log.quick_note = data.quick_note
        await db.flush()
        await db.refresh(pending_log)
        logger.info("Check-in direspons: user_id=%s, log_id=%s", user_id, pending_log.id)
        return pending_log
    else:
        # Buat check-in baru
        log = SafePingLog(
            user_id=user_id,
            scheduled_at=now,
            responded_at=now,
            status="responded",
            mood_score=data.mood_score,
            quick_note=data.quick_note,
        )
        db.add(log)
        await db.flush()
        await db.refresh(log)
        logger.info("Check-in baru dibuat: user_id=%s", user_id)
        return log


async def get_checkin_history(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 30,
    offset: int = 0,
) -> List[SafePingLog]:
    """Ambil riwayat check-in."""
    result = await db.execute(
        select(SafePingLog)
        .where(SafePingLog.user_id == user_id)
        .order_by(desc(SafePingLog.scheduled_at))
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


async def escalate_missed_checkin(db: AsyncSession, user_id: UUID, log_id: UUID) -> None:
    """Eskalasi check-in yang tidak direspons."""
    result = await db.execute(
        select(SafePingLog).where(SafePingLog.id == log_id)
    )
    log = result.scalar_one_or_none()
    if not log:
        return

    # Ambil konfigurasi
    config = await get_safeping_config(db, user_id)

    now = datetime.now(timezone.utc)

    if config.escalation_to_emergency_contacts:
        # Ambil kontak darurat
        contacts_result = await db.execute(
            select(EmergencyContact).where(
                and_(
                    EmergencyContact.user_id == user_id,
                    EmergencyContact.is_active == True,  # noqa: E712
                )
            ).order_by(EmergencyContact.priority)
        )
        contacts = contacts_result.scalars().all()

        if contacts:
            contact_list = [
                {"name": c.name, "phone": c.phone} for c in contacts
            ]
            await notification_service.notify_emergency_contacts(
                user_id=user_id,
                contacts=contact_list,
                event_type="safeping_missed",
                message="Pengguna JagaDiri belum melakukan check-in hari ini. "
                "Mohon periksa kondisi beliau.",
            )
            log.status = "escalated_contact"
            log.escalation_sent_at = now

    if config.escalation_to_119:
        await notification_service.notify_119(
            user_id=user_id,
            latitude=None,
            longitude=None,
            address=None,
        )
        log.status = "escalated_119"
        log.escalation_sent_at = now

    await db.flush()
    logger.warning("Check-in eskalasi: user_id=%s, status=%s", user_id, log.status)


# ── SOS ──────────────────────────────────────────────────────────────────────


async def trigger_sos(
    db: AsyncSession, user_id: UUID, data: SOSRequest
) -> SOSEvent:
    """Aktifkan SOS darurat."""

    now = datetime.now(timezone.utc)

    # Ambil kontak darurat
    contacts_result = await db.execute(
        select(EmergencyContact).where(
            and_(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_active == True,  # noqa: E712
            )
        ).order_by(EmergencyContact.priority)
    )
    contacts = contacts_result.scalars().all()

    # Notifikasi kontak darurat
    notified_contacts = []
    if contacts:
        contact_list = [{"name": c.name, "phone": c.phone} for c in contacts]
        notified_contacts = await notification_service.notify_emergency_contacts(
            user_id=user_id,
            contacts=contact_list,
            event_type="sos",
            message="🚨 DARURAT: Pengguna JagaDiri mengaktifkan SOS! "
            f"Lokasi: {data.address_snapshot or 'Tidak tersedia'}",
        )

    # Notifikasi 119
    service_119 = False
    config = await get_safeping_config(db, user_id)
    if config.escalation_to_119:
        await notification_service.notify_119(
            user_id=user_id,
            latitude=data.latitude,
            longitude=data.longitude,
            address=data.address_snapshot,
        )
        service_119 = True

    # Buat event SOS
    sos_event = SOSEvent(
        user_id=user_id,
        triggered_at=now,
        latitude=data.latitude,
        longitude=data.longitude,
        address_snapshot=data.address_snapshot,
        status="active",
        contacts_notified={"contacts": notified_contacts},
        service_119_notified=service_119,
    )
    db.add(sos_event)
    await db.flush()
    await db.refresh(sos_event)

    logger.critical("🚨 SOS DIAKTIFKAN: user_id=%s, sos_id=%s", user_id, sos_event.id)
    return sos_event


async def resolve_sos(
    db: AsyncSession, user_id: UUID, sos_id: UUID, data: SOSResolveRequest
) -> SOSEvent:
    """Selesaikan event SOS."""
    result = await db.execute(
        select(SOSEvent).where(
            and_(
                SOSEvent.id == sos_id,
                SOSEvent.user_id == user_id,
            )
        )
    )
    sos = result.scalar_one_or_none()
    if not sos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event SOS tidak ditemukan.",
        )

    if sos.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event SOS ini sudah diselesaikan.",
        )

    sos.status = data.status
    sos.resolved_at = datetime.now(timezone.utc)
    sos.resolution_note = data.resolution_note

    await db.flush()
    await db.refresh(sos)
    logger.info("SOS diselesaikan: sos_id=%s, status=%s", sos_id, data.status)
    return sos


async def get_sos_history(
    db: AsyncSession, user_id: UUID, limit: int = 20, offset: int = 0
) -> List[SOSEvent]:
    """Ambil riwayat SOS."""
    result = await db.execute(
        select(SOSEvent)
        .where(SOSEvent.user_id == user_id)
        .order_by(desc(SOSEvent.triggered_at))
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())

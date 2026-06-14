"""
JagaDiri — Layanan Portal Keluarga
Business logic untuk portal keluarga, undangan koneksi, dan izin berbagi data.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family import FamilyConnection
from app.models.user import User
from app.models.safeping import SafePingLog
from app.models.medication import MedicationAdherenceLog, MedicationReminder
from app.models.health_record import VitalSign
from app.schemas.family import (
    FamilyInviteRequest,
    FamilyPermissionUpdate,
    FamilyMemberStatusResponse,
)

logger = logging.getLogger("jagadiri.family")


async def send_invite(
    db: AsyncSession, user_id: UUID, data: FamilyInviteRequest
) -> FamilyConnection:
    """Kirim undangan koneksi ke anggota keluarga berdasarkan email."""

    # Cari user keluarga yang diundang
    result = await db.execute(select(User).where(User.email == data.email))
    family_member = result.scalar_one_or_none()
    if not family_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email anggota keluarga tidak terdaftar di platform JagaDiri.",
        )

    if family_member.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anda tidak dapat mengundang diri Anda sendiri.",
        )

    # Cek apakah koneksi sudah ada
    conn_result = await db.execute(
        select(FamilyConnection).where(
            and_(
                FamilyConnection.user_id == user_id,
                FamilyConnection.family_member_id == family_member.id,
            )
        )
    )
    existing = conn_result.scalar_one_or_none()
    if existing:
        if existing.status == "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Koneksi keluarga dengan akun ini sudah aktif.",
            )
        elif existing.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Undangan ke email ini sudah dikirim dan berstatus pending.",
            )
        else:
            # Re-activate jika sebelumnya revoked
            existing.status = "pending"
            existing.relation = data.relation
            existing.access_level = data.access_level
            existing.can_view_safeping = data.can_view_safeping
            existing.can_view_medication_adherence = data.can_view_medication_adherence
            existing.can_view_vital_signs = data.can_view_vital_signs
            existing.can_view_consultation_history = data.can_view_consultation_history
            existing.can_view_mental_health = data.can_view_mental_health
            await db.flush()
            return existing

    connection = FamilyConnection(
        user_id=user_id,
        family_member_id=family_member.id,
        relation=data.relation,
        access_level=data.access_level,
        can_view_safeping=data.can_view_safeping,
        can_view_medication_adherence=data.can_view_medication_adherence,
        can_view_vital_signs=data.can_view_vital_signs,
        can_view_consultation_history=data.can_view_consultation_history,
        can_view_mental_health=data.can_view_mental_health,
        status="pending",
    )
    db.add(connection)
    await db.flush()
    logger.info("Undangan keluarga dikirim: dari %s ke %s", user_id, family_member.id)
    return connection


async def list_connections(
    db: AsyncSession, user_id: UUID
) -> List[FamilyConnection]:
    """Ambil daftar koneksi keluarga (yang diundang atau mengundang)."""
    result = await db.execute(
        select(FamilyConnection)
        .where(
            or_(
                FamilyConnection.user_id == user_id,
                FamilyConnection.family_member_id == user_id,
            )
        )
    )
    connections = result.scalars().all()
    
    # Resolusi nama anggota keluarga
    for conn in connections:
        target_id = conn.family_member_id if conn.user_id == user_id else conn.user_id
        usr_res = await db.execute(select(User).where(User.id == target_id))
        usr = usr_res.scalar_one_or_none()
        if usr:
            conn.family_member_name = usr.full_name
            
    return list(connections)


async def accept_invite(
    db: AsyncSession, user_id: UUID, connection_id: UUID
) -> FamilyConnection:
    """Terima undangan koneksi keluarga."""
    result = await db.execute(
        select(FamilyConnection).where(
            and_(
                FamilyConnection.id == connection_id,
                FamilyConnection.family_member_id == user_id,
            )
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Undangan tidak ditemukan.",
        )

    if conn.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Undangan ini tidak dapat diterima karena berstatus " + conn.status,
        )

    conn.status = "active"
    conn.connected_at = datetime.now(timezone.utc)
    await db.flush()
    logger.info("Koneksi keluarga aktif: connection_id=%s", connection_id)
    return conn


async def update_permissions(
    db: AsyncSession, user_id: UUID, connection_id: UUID, data: FamilyPermissionUpdate
) -> FamilyConnection:
    """Perbarui izin berbagi data (hanya oleh pasien/pemilik data)."""
    result = await db.execute(
        select(FamilyConnection).where(
            and_(
                FamilyConnection.id == connection_id,
                FamilyConnection.user_id == user_id,
            )
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Koneksi keluarga tidak ditemukan.",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conn, field, value)

    await db.flush()
    await db.refresh(conn)
    logger.info("Izin koneksi keluarga diperbarui: connection_id=%s", connection_id)
    return conn


async def get_member_status(
    db: AsyncSession, family_user_id: UUID, patient_id: UUID
) -> FamilyMemberStatusResponse:
    """Ambil status kesehatan anggota keluarga (untuk pemantauan)."""
    
    # Pastikan koneksi aktif
    result = await db.execute(
        select(FamilyConnection).where(
            and_(
                FamilyConnection.user_id == patient_id,
                FamilyConnection.family_member_id == family_user_id,
                FamilyConnection.status == "active",
            )
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses aktif ke data pengguna ini.",
        )

    # Ambil info pengguna
    user_result = await db.execute(select(User).where(User.id == patient_id))
    patient = user_result.scalar_one()

    safeping_status = None
    last_check_in = None
    medication_adherence = None
    last_vital = None

    # Status SafePing
    if conn.can_view_safeping:
        ping_result = await db.execute(
            select(SafePingLog)
            .where(SafePingLog.user_id == patient_id)
            .order_by(desc(SafePingLog.scheduled_at))
            .limit(1)
        )
        last_ping = ping_result.scalar_one_or_none()
        if last_ping:
            safeping_status = last_ping.status
            last_check_in = last_ping.responded_at

    # Kepatuhan Obat (30 hari)
    if conn.can_view_medication_adherence:
        from app.services.medication_service import get_adherence_report
        try:
            report = await get_adherence_report(db, patient_id)
            medication_adherence = report.persentase_kepatuhan
        except Exception:
            medication_adherence = 0.0

    # Tanda Vital Terakhir
    if conn.can_view_vital_signs:
        vital_result = await db.execute(
            select(VitalSign)
            .where(VitalSign.user_id == patient_id)
            .order_by(desc(VitalSign.created_at))
            .limit(1)
        )
        last_v = vital_result.scalar_one_or_none()
        if last_v:
            last_vital = {
                "metric_type": last_v.metric_type,
                "value_numeric": float(last_v.value_numeric) if last_v.value_numeric else None,
                "value_systolic": last_v.value_systolic,
                "value_diastolic": last_v.value_diastolic,
                "unit": last_v.unit,
                "created_at": last_v.created_at,
            }

    return FamilyMemberStatusResponse(
        user_id=patient_id,
        full_name=patient.full_name,
        safeping_status=safeping_status,
        last_check_in=last_check_in,
        medication_adherence_pct=medication_adherence,
        last_vital_signs=last_vital,
    )

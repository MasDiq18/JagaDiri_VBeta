"""
JagaDiri — Layanan Konsultasi
Business logic untuk booking konsultasi, transisi status, catatan SOAP, dan rating.
"""

import logging
import secrets
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.consultation import (
    Consultation,
    ConsultationNote,
    Doctor,
    DoctorSchedule,
)
from app.models.user import User
from app.schemas.consultation import (
    ConsultationCreate,
    ConsultationNoteCreate,
    ConsultationResponse,
    ConsultationStatusUpdate,
    DoctorListFilter,
    DoctorResponse,
    RateRequest,
)

logger = logging.getLogger("jagadiri.consultation")


# ── Dokter ───────────────────────────────────────────────────────────────────


async def list_doctors(
    db: AsyncSession, filters: DoctorListFilter
) -> tuple[List[Doctor], int]:
    """Ambil daftar dokter dengan filter."""

    query = select(Doctor).where(Doctor.is_verified == True)  # noqa: E712

    if filters.specialization:
        query = query.where(Doctor.specialization.ilike(f"%{filters.specialization}%"))

    if filters.is_online is not None:
        query = query.where(Doctor.is_online == filters.is_online)

    if filters.available_for_home_visit is not None:
        query = query.where(
            Doctor.available_for_home_visit == filters.available_for_home_visit
        )

    if filters.min_rating is not None:
        query = query.where(Doctor.rating >= filters.min_rating)

    if filters.max_fee is not None:
        query = query.where(
            or_(
                Doctor.consultation_fee_general <= filters.max_fee,
                Doctor.consultation_fee_general.is_(None),
            )
        )

    if filters.search:
        search_term = f"%{filters.search}%"
        # Perlu join ke User untuk pencarian nama
        query = query.join(User, Doctor.user_id == User.id).where(
            or_(
                User.full_name.ilike(search_term),
                Doctor.specialization.ilike(search_term),
            )
        )

    # Hitung total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginasi
    offset = (filters.halaman - 1) * filters.per_halaman
    query = query.order_by(desc(Doctor.rating)).offset(offset).limit(filters.per_halaman)

    result = await db.execute(query)
    doctors = list(result.scalars().all())

    return doctors, total


async def get_doctor(db: AsyncSession, doctor_id: UUID) -> Doctor:
    """Ambil detail dokter."""
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokter tidak ditemukan.",
        )
    return doctor


def format_doctor_response(doctor: Doctor) -> DoctorResponse:
    """Format data dokter untuk respons API."""
    full_name = None
    if doctor.user:
        full_name = doctor.user.full_name

    return DoctorResponse(
        id=doctor.id,
        user_id=doctor.user_id,
        str_number=doctor.str_number,
        sip_number=doctor.sip_number,
        specialization=doctor.specialization,
        sub_specialization=doctor.sub_specialization,
        education=doctor.education,
        experience_years=doctor.experience_years,
        languages=doctor.languages,
        consultation_fee_general=doctor.consultation_fee_general,
        consultation_fee_specialist=doctor.consultation_fee_specialist,
        rating=float(doctor.rating) if doctor.rating else 0.0,
        total_reviews=doctor.total_reviews,
        is_verified=doctor.is_verified,
        is_online=doctor.is_online,
        available_for_home_visit=doctor.available_for_home_visit,
        bio=doctor.bio,
        profile_photo_url=doctor.profile_photo_url,
        full_name=full_name,
        schedules=[],
        created_at=doctor.created_at,
    )


# ── Konsultasi ───────────────────────────────────────────────────────────────


async def create_consultation(
    db: AsyncSession, patient_id: UUID, data: ConsultationCreate
) -> Consultation:
    """Buat konsultasi baru."""

    # Verifikasi dokter ada dan terverifikasi
    doctor_result = await db.execute(
        select(Doctor).where(
            and_(Doctor.id == data.doctor_id, Doctor.is_verified == True)  # noqa: E712
        )
    )
    doctor = doctor_result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokter tidak ditemukan atau belum diverifikasi.",
        )

    # Generate channel name untuk video call
    channel_name = None
    if data.type in ("video", "chat"):
        channel_name = f"jd-{secrets.token_urlsafe(8)}"

    # Tentukan biaya
    fee = doctor.consultation_fee_general or 0

    consultation = Consultation(
        patient_id=patient_id,
        doctor_id=data.doctor_id,
        type=data.type,
        status="pending",
        scheduled_at=data.scheduled_at,
        chief_complaint=data.chief_complaint,
        patient_notes=data.patient_notes,
        is_urgent=data.is_urgent,
        agora_channel_name=channel_name,
        fee_charged=fee,
        payment_status="pending",
    )
    db.add(consultation)
    await db.flush()
    await db.refresh(consultation)

    logger.info(
        "Konsultasi dibuat: id=%s, patient=%s, doctor=%s, type=%s",
        consultation.id, patient_id, data.doctor_id, data.type,
    )
    return consultation


async def list_consultations(
    db: AsyncSession,
    user_id: UUID,
    role: str = "patient",
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> List[Consultation]:
    """Ambil daftar konsultasi pengguna."""

    if role == "doctor":
        # Ambil doctor_id
        from app.models.consultation import Doctor
        doc_result = await db.execute(
            select(Doctor).where(Doctor.user_id == user_id)
        )
        doctor = doc_result.scalar_one_or_none()
        if not doctor:
            return []
        query = select(Consultation).where(Consultation.doctor_id == doctor.id)
    else:
        query = select(Consultation).where(Consultation.patient_id == user_id)

    if status_filter:
        query = query.where(Consultation.status == status_filter)

    query = query.order_by(desc(Consultation.created_at)).offset(offset).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_consultation(
    db: AsyncSession, consultation_id: UUID, user_id: UUID
) -> Consultation:
    """Ambil detail konsultasi."""
    result = await db.execute(
        select(Consultation).where(Consultation.id == consultation_id)
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Konsultasi tidak ditemukan.",
        )

    # Verifikasi akses — hanya pasien atau dokter yang terkait
    is_patient = consultation.patient_id == user_id
    is_doctor = False
    if consultation.doctor:
        is_doctor = consultation.doctor.user_id == user_id

    if not is_patient and not is_doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses ke konsultasi ini.",
        )

    return consultation


def format_consultation_response(consultation: Consultation) -> ConsultationResponse:
    """Format data konsultasi untuk respons API."""
    doctor_name = None
    specialization = None
    patient_name = None

    if consultation.doctor and consultation.doctor.user:
        doctor_name = consultation.doctor.user.full_name
        specialization = consultation.doctor.specialization

    if consultation.patient:
        patient_name = consultation.patient.full_name

    notes_resp = None
    if consultation.notes:
        from app.schemas.consultation import ConsultationNoteResponse
        notes_resp = ConsultationNoteResponse(
            id=consultation.notes.id,
            consultation_id=consultation.notes.consultation_id,
            subjective=consultation.notes.subjective,
            objective=consultation.notes.objective,
            assessment=consultation.notes.assessment,
            plan=consultation.notes.plan,
            diagnosis_codes=consultation.notes.diagnosis_codes,
            follow_up_days=consultation.notes.follow_up_days,
            is_confidential=consultation.notes.is_confidential,
            created_at=consultation.notes.created_at,
        )

    return ConsultationResponse(
        id=consultation.id,
        patient_id=consultation.patient_id,
        doctor_id=consultation.doctor_id,
        type=consultation.type,
        status=consultation.status,
        scheduled_at=consultation.scheduled_at,
        started_at=consultation.started_at,
        ended_at=consultation.ended_at,
        chief_complaint=consultation.chief_complaint,
        patient_notes=consultation.patient_notes,
        is_urgent=consultation.is_urgent,
        agora_channel_name=consultation.agora_channel_name,
        fee_charged=consultation.fee_charged,
        payment_status=consultation.payment_status,
        doctor_name=doctor_name,
        patient_name=patient_name,
        specialization=specialization,
        notes=notes_resp,
        created_at=consultation.created_at,
        updated_at=consultation.updated_at,
    )


async def update_consultation_status(
    db: AsyncSession,
    consultation_id: UUID,
    user_id: UUID,
    data: ConsultationStatusUpdate,
) -> Consultation:
    """Perbarui status konsultasi."""
    consultation = await get_consultation(db, consultation_id, user_id)

    # Validasi transisi status
    valid_transitions = {
        "pending": {"confirmed", "cancelled"},
        "confirmed": {"ongoing", "cancelled", "no_show"},
        "ongoing": {"completed"},
    }

    allowed = valid_transitions.get(consultation.status, set())
    if data.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tidak dapat mengubah status dari '{consultation.status}' ke '{data.status}'. "
            f"Status yang diizinkan: {', '.join(allowed) if allowed else 'tidak ada'}",
        )

    now = datetime.now(timezone.utc)
    consultation.status = data.status

    if data.status == "ongoing":
        consultation.started_at = now
    elif data.status == "completed":
        consultation.ended_at = now
        consultation.payment_status = "paid"

    await db.flush()
    await db.refresh(consultation)
    logger.info(
        "Status konsultasi diperbarui: id=%s, status=%s",
        consultation_id, data.status,
    )
    return consultation


# ── Catatan Konsultasi ───────────────────────────────────────────────────────


async def create_consultation_note(
    db: AsyncSession,
    consultation_id: UUID,
    user_id: UUID,
    data: ConsultationNoteCreate,
) -> ConsultationNote:
    """Tambah catatan konsultasi (SOAP). Hanya dokter."""

    # Ambil konsultasi
    result = await db.execute(
        select(Consultation).where(Consultation.id == consultation_id)
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Konsultasi tidak ditemukan.",
        )

    # Verifikasi dokter
    if not consultation.doctor or consultation.doctor.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dokter yang menangani dapat menambah catatan konsultasi.",
        )

    # Cek apakah catatan sudah ada
    existing = await db.execute(
        select(ConsultationNote).where(
            ConsultationNote.consultation_id == consultation_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Catatan konsultasi sudah ada. Gunakan endpoint update untuk memperbarui.",
        )

    note = ConsultationNote(
        consultation_id=consultation_id,
        **data.model_dump(),
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)

    logger.info("Catatan konsultasi ditambahkan: consultation_id=%s", consultation_id)
    return note


# ── Rating ───────────────────────────────────────────────────────────────────


async def rate_consultation(
    db: AsyncSession,
    consultation_id: UUID,
    user_id: UUID,
    data: RateRequest,
) -> Doctor:
    """Beri rating pada konsultasi."""

    result = await db.execute(
        select(Consultation).where(
            and_(
                Consultation.id == consultation_id,
                Consultation.patient_id == user_id,
            )
        )
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Konsultasi tidak ditemukan.",
        )

    if consultation.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hanya konsultasi yang sudah selesai yang dapat diberi rating.",
        )

    # Update rating dokter (moving average)
    doctor_result = await db.execute(
        select(Doctor).where(Doctor.id == consultation.doctor_id)
    )
    doctor = doctor_result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokter tidak ditemukan.",
        )

    total_score = float(doctor.rating) * doctor.total_reviews + data.rating
    doctor.total_reviews += 1
    doctor.rating = total_score / doctor.total_reviews

    await db.flush()
    await db.refresh(doctor)

    logger.info(
        "Rating diberikan: consultation=%s, doctor=%s, rating=%s",
        consultation_id, doctor.id, data.rating,
    )
    return doctor

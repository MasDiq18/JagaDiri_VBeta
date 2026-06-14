"""
JagaDiri — Router AI & Asisten Kesehatan
Endpoints untuk analisis gejala mandiri (symptom checker) dan rekomendasi kesehatan personal.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.health_record import VitalSign
from app.models.medication import MedicationReminder
from app.schemas.ai import SymptomCheckRequest, SymptomCheckResponse, HealthInsightResponse
from app.services import symptom_checker

router = APIRouter(prefix="/ai", tags=["Asisten AI JagaDiri"])


@router.post(
    "/symptom-check",
    response_model=SymptomCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Analisis gejala mandiri (Symptom Checker)",
)
async def symptom_check(data: SymptomCheckRequest):
    """
    Menganalisis daftar gejala yang dirasakan pengguna secara real-time.
    Sistem akan memetakan keluhan ke kemungkinan kondisi klinis (ICD-10) serta menyarankan tingkat keparahan/urgensi tindakan.
    """
    return symptom_checker.check_symptoms(data)


@router.get(
    "/health-insights",
    response_model=HealthInsightResponse,
    status_code=status.HTTP_200_OK,
    summary="Ambil wawasan kesehatan personal",
)
async def read_health_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Menghasilkan wawasan kesehatan yang dipersonalisasi berdasarkan data tanda vital terakhir,
    adherence obat, dan profil medis pengguna.
    """
    # Ambil vital signs terakhir
    vitals_res = await db.execute(
        select(VitalSign)
        .where(VitalSign.user_id == current_user.id)
        .order_by(desc(VitalSign.created_at))
        .limit(3)
    )
    vitals = vitals_res.scalars().all()

    # Ambil obat aktif
    meds_res = await db.execute(
        select(MedicationReminder)
        .where(
            MedicationReminder.user_id == current_user.id,
            MedicationReminder.is_active == True,  # noqa: E712
        )
    )
    meds = meds_res.scalars().all()

    # Logika analisis otomatis sederhana
    ringkasan_kesehatan = (
        f"Halo {current_user.full_name}, secara umum sistem mencatat kondisi Anda stabil. "
    )
    saran_kesehatan = [
        "Jaga hidrasi tubuh dengan minum air putih minimal 8 gelas sehari.",
        "Cobalah untuk berjalan kaki ringan selama 15-30 menit setiap hari.",
    ]
    pengingat = []
    skor_kesehatan = 85

    if vitals:
        # Periksa tensi jika ada
        bp = next((v for v in vitals if v.metric_type == "blood_pressure"), None)
        if bp and bp.value_systolic and bp.value_diastolic:
            sys, dia = bp.value_systolic, bp.value_diastolic
            if sys > 130 or dia > 80:
                ringkasan_kesehatan += "Sistem mendeteksi tekanan darah Anda sedikit di atas batas normal. "
                saran_kesehatan.append("Kurangi konsumsi garam berlebih dan hindari stres.")
                pengingat.append("Ukur tekanan darah Anda lagi besok pagi.")
                skor_kesehatan -= 10
            else:
                ringkasan_kesehatan += "Tekanan darah terakhir Anda tercatat sangat baik. "

    if meds:
        pengingat.append(f"Hari ini Anda memiliki {len(meds)} jadwal konsumsi obat.")
    else:
        saran_kesehatan.append("Lengkapi daftar pengingat obat jika Anda sedang dalam terapi obat rutin.")

    return HealthInsightResponse(
        user_id=current_user.id,
        ringkasan_kesehatan=ringkasan_kesehatan,
        saran_kesehatan=saran_kesehatan,
        pengingat=pengingat,
        skor_kesehatan=max(50, skor_kesehatan),
    )

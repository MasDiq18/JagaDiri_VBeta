"""
JagaDiri — Database Seeding
Membuat data sampel untuk Dokter dan Pengguna di Indonesia jika database kosong.
"""

import logging
import uuid
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserMedicalProfile
from app.models.safeping import SafePingConfig
from app.models.consultation import Doctor

logger = logging.getLogger("jagadiri.seed")


async def seed_all_data(db: AsyncSession):
    """Menjalankan seeding untuk data awal."""
    
    # Cek apakah database sudah berisi data user
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        logger.info("Database sudah berisi data. Melewati proses seeding.")
        return

    logger.info("Database kosong. Memulai seeding data awal JagaDiri...")

    # === 1. Seed Patient Users ===
    patients_data = [
        {
            "email": "budi@jagadiri.id",
            "full_name": "Budi Santoso",
            "phone": "+6281234567890",
            "gender": "male",
            "date_of_birth": date(1995, 8, 17),
            "nik": "3171011708950001",
        },
        {
            "email": "siti@jagadiri.id",
            "full_name": "Siti Aminah",
            "phone": "+6282245678901",
            "gender": "female",
            "date_of_birth": date(1948, 5, 2), # Lansia tinggal mandiri
            "nik": "3171020205480002",
        },
        {
            "email": "andi@jagadiri.id",
            "full_name": "Andi Wijaya",
            "phone": "+6283876543210",
            "gender": "male",
            "date_of_birth": date(2002, 11, 30), # Mahasiswa perantau
            "nik": "3171033011020003",
        }
    ]

    patients = []
    pwd = hash_password("JagaDiri2026!")

    for p_info in patients_data:
        u = User(
            email=p_info["email"],
            password_hash=pwd,
            full_name=p_info["full_name"],
            phone=p_info["phone"],
            gender=p_info["gender"],
            date_of_birth=p_info["date_of_birth"],
            nik=p_info["nik"],
            onboarding_completed=True,
            is_verified=True,
        )
        db.add(u)
        patients.append(u)

    await db.flush()

    # Buat profil medis & config SafePing untuk pasien
    for u in patients:
        med_prof = UserMedicalProfile(user_id=u.id)
        # Khusus untuk Ibu Siti (Lansia)
        if u.email == "siti@jagadiri.id":
            med_prof.blood_type = "O+"
            med_prof.allergies = ["Udang", "Debu"]
            med_prof.chronic_conditions = ["Hipertensi", "Osteoarthritis"]
            med_prof.emergency_contact_name = "Rahmat Wijaya"
            med_prof.emergency_contact_phone = "+628111222333"
            med_prof.emergency_contact_relation = "Anak Kandung"
            med_prof.bpjs_number = "0001234567890"

        db.add(med_prof)
        db.add(SafePingConfig(user_id=u.id))

    # === 2. Seed Doctor Users & Profiles ===
    doctors_data = [
        {
            "name": "dr. Rian Pratama",
            "email": "dr.rian@jagadiri.id",
            "phone": "+6289911122201",
            "spec": "Dokter Umum",
            "sub_spec": "Pelayanan Primer",
            "experience": 5,
            "fee": 35000,
            "bio": "Dokter umum yang berdedikasi tinggi untuk pencegahan penyakit dan gaya hidup sehat di lingkungan urban.",
        },
        {
            "name": "dr. Indah Lestari, Sp.PD",
            "email": "dr.indah@jagadiri.id",
            "phone": "+6289911122202",
            "spec": "Spesialis Penyakit Dalam",
            "sub_spec": "Gastroenterologi",
            "experience": 8,
            "fee": 80000,
            "bio": "Spesialis Penyakit Dalam dengan fokus pada keluhan pencernaan kronis, sindrom metabolik, dan diabetes melitus.",
        },
        {
            "name": "dr. Ahmad Fauzi, Sp.JP",
            "email": "dr.ahmad@jagadiri.id",
            "phone": "+6289911122203",
            "spec": "Kardiologi",
            "sub_spec": "Penyakit Jantung Koroner",
            "experience": 12,
            "fee": 120000,
            "bio": "Spesialis Jantung dan Pembuluh Darah dengan keahlian penanganan aritmia, gagal jantung, dan pemulihan pasca-stroke.",
        },
        {
            "name": "dr. Maya Sari, Sp.N",
            "email": "dr.maya@jagadiri.id",
            "phone": "+6289911122204",
            "spec": "Neurologi",
            "sub_spec": "Saraf Kejepit & Stroke",
            "experience": 10,
            "fee": 85000,
            "bio": "Membantu pasien mengelola sakit kepala migrain kronis, vertigo, penyakit Parkinson, dan rehabilitasi saraf.",
        },
        {
            "name": "dr. Joko Susilo, Sp.KJ",
            "email": "dr.joko@jagadiri.id",
            "phone": "+6289911122205",
            "spec": "Psikiater",
            "sub_spec": "Depresi & Gangguan Kecemasan",
            "experience": 15,
            "fee": 90000,
            "bio": "Ahli kesehatan mental yang berfokus pada terapi kognitif perilaku untuk mengatasi stres isolasi sosial dan kecemasan urban.",
        },
        {
            "name": "dr. Fitri Handayani, Sp.OG",
            "email": "dr.fitri@jagadiri.id",
            "phone": "+6289911122206",
            "spec": "Obstetri & Ginekologi",
            "sub_spec": "Kehamilan Berisiko Tinggi",
            "experience": 9,
            "fee": 95000,
            "bio": "Pendamping kehamilan terpercaya, berfokus membantu ibu hamil tunggal melalui edukasi persalinan aman.",
        },
        {
            "name": "dr. Hendra Wijaya, Sp.A",
            "email": "dr.hendra@jagadiri.id",
            "phone": "+6289911122207",
            "spec": "Anak",
            "sub_spec": "Tumbuh Kembang Anak",
            "experience": 11,
            "fee": 75000,
            "bio": "Spesialis kesehatan anak terkemuka dengan keahlian imunisasi dasar, gizi anak, dan penanganan demam anak.",
        },
        {
            "name": "dr. Dewi Lestari, Sp.M",
            "email": "dr.dewi@jagadiri.id",
            "phone": "+6289911122208",
            "spec": "Mata",
            "sub_spec": "Retina & Katarak",
            "experience": 7,
            "fee": 70000,
            "bio": "Menangani gangguan refraksi mata akibat penggunaan gawai berlebih serta pencegahan glaukoma.",
        },
        {
            "name": "dr. Bambang Hermawan, Sp.THT-KL",
            "email": "dr.bambang@jagadiri.id",
            "phone": "+6289911122209",
            "spec": "THT",
            "sub_spec": "Audiologi",
            "experience": 14,
            "fee": 85000,
            "bio": "Spesialis Telinga Hidung Tenggorokan dengan keahlian menangani sinusitis kronis dan infeksi telinga tengah.",
        },
        {
            "name": "dr. Lusi Rahmawati, Sp.KK",
            "email": "dr.lusi@jagadiri.id",
            "phone": "+6289911122210",
            "spec": "Kulit & Kelamin",
            "sub_spec": "Dermatologi Estetik & Infeksi",
            "experience": 6,
            "fee": 75000,
            "bio": "Membantu pasien mengobati dermatitis atopik, jerawat parah, infeksi jamur kulit, dan alergi kulit.",
        },
        {
            "name": "dr. Anton Budiman, Sp.OT",
            "email": "dr.anton@jagadiri.id",
            "phone": "+6289911122211",
            "spec": "Ortopedi",
            "sub_spec": "Traumatologi & Sendi",
            "experience": 13,
            "fee": 110000,
            "bio": "Fokus pada penanganan patah tulang, radang sendi lutut, cedera olahraga, dan fisioterapi tulang belakang.",
        },
        {
            "name": "dr. Riza Fahri, Sp.P",
            "email": "dr.riza@jagadiri.id",
            "phone": "+6289911122212",
            "spec": "Paru",
            "sub_spec": "Asma & Bronkitis Kronis",
            "experience": 10,
            "fee": 85000,
            "bio": "Spesialis paru untuk konsultasi tuberkulosis (TBC), infeksi paru pneumonia, dan batuk kronis.",
        }
    ]

    for d_idx, d_info in enumerate(doctors_data):
        # 2a. Buat user untuk dokter
        u_doc = User(
            email=d_info["email"],
            password_hash=pwd,
            full_name=d_info["name"],
            phone=d_info["phone"],
            onboarding_completed=True,
            is_verified=True,
            subscription_tier="basic", # Dokter menggunakan tier dasar
        )
        db.add(u_doc)
        await db.flush()

        # 2b. Buat profil dokter
        doc_prof = Doctor(
            user_id=u_doc.id,
            str_number=f"STR-{12345678 + d_idx}",
            sip_number=f"SIP-{87654321 + d_idx}",
            specialization=d_info["spec"],
            sub_specialization=d_info["sub_spec"],
            experience_years=d_info["experience"],
            consultation_fee_general=d_info["fee"],
            consultation_fee_specialist=d_info["fee"] + 20000,
            rating=4.5 + (d_idx % 6) * 0.1,  # 4.5, 4.6, 4.7, 4.8, 4.9, 5.0
            total_reviews=10 + d_idx * 5,
            is_verified=True,
            is_online=(d_idx % 2 == 0),  # Selang-seling online/offline
            available_for_home_visit=(d_idx % 3 == 0),
            bio=d_info["bio"],
            education=["Fakultas Kedokteran Universitas Indonesia", "Spesialisasi Kolegium Kedokteran Indonesia"],
        )
        db.add(doc_prof)

    await db.flush()
    logger.info("Seeding berhasil! 3 akun pasien dan 12 akun dokter telah dibuat.")

"""
JagaDiri — Layanan Analisis Gejala (Symptom Checker)
Business logic berbasis aturan untuk menganalisis gejala dalam Bahasa Indonesia
dan memetakan ke kemungkinan penyakit/kondisi medis (ICD-10).
"""

import logging
from typing import List, Optional
from uuid import UUID

from app.schemas.ai import SymptomCheckRequest, SymptomCheckResponse, PossibleCondition

logger = logging.getLogger("jagadiri.ai")

# Kamus pemetaan gejala ke kondisi medis
RULES = [
    {
        "keywords": ["nyeri dada", "sakit dada", "sesak nafas", "sesak napas", "dada berdebar", "jantung berdebar"],
        "conditions": [
            {
                "nama_kondisi": "Penyakit Jantung Koroner / Angina",
                "nama_kondisi_medis": "Coronary Artery Disease / Angina Pectoris",
                "kode_icd10": "I25.1",
                "probabilitas": "sedang",
                "penjelasan": "Penyempitan pembuluh darah jantung yang menghambat aliran darah ke otot jantung.",
                "saran_tindakan": "SEGERA pergi ke Unit Gawat Darurat (UGD) terdekat. Jangan mengemudi sendiri.",
            },
            {
                "nama_kondisi": "Asma Bronkial (Kekambuhan)",
                "nama_kondisi_medis": "Asthma Exacerbation",
                "kode_icd10": "J45.9",
                "probabilitas": "tinggi",
                "penjelasan": "Penyempitan dan peradangan pada saluran pernapasan yang dipicu oleh alergen atau aktivitas fisik.",
                "saran_tindakan": "Gunakan inhaler pelega Anda segera. Jika sesak berlanjut, hubungi kontak darurat.",
            }
        ],
        "urgensi": "darurat",
        "saran_umum": "Gejala yang Anda rasakan merupakan indikasi gangguan kardiovaskular atau pernapasan akut yang berpotensi mengancam jiwa. Hubungi 119 atau segera menuju IGD rumah sakit terdekat."
    },
    {
        "keywords": ["demam", "panas", "menggigil", "badan hangat", "suhu tinggi"],
        "conditions": [
            {
                "nama_kondisi": "Demam Berdarah Dengue (DBD)",
                "nama_kondisi_medis": "Dengue Hemorrhagic Fever",
                "kode_icd10": "A90",
                "probabilitas": "sedang",
                "penjelasan": "Penyakit akibat virus Dengue yang ditularkan lewat gigitan nyamuk Aedes aegypti.",
                "saran_tindakan": "Perbanyak minum air putih, konsumsi parasetamol untuk demam, dan lakukan tes darah jika demam berlanjut lebih dari 3 hari.",
            },
            {
                "nama_kondisi": "Infeksi Saluran Pernapasan Akut (ISPA)",
                "nama_kondisi_medis": "Acute Upper Respiratory Infection",
                "kode_icd10": "J06.9",
                "probabilitas": "tinggi",
                "penjelasan": "Infeksi virus atau bakteri pada saluran pernapasan bagian atas.",
                "saran_tindakan": "Istirahat cukup, konsumsi air hangat, dan minum parasetamol bila demam tinggi.",
            }
        ],
        "urgensi": "sedang",
        "saran_umum": "Pantau suhu tubuh secara berkala. Pastikan hidrasi tercukupi dengan minum air minimal 2 liter per hari. Hubungi dokter jika demam melebihi 39 derajat Celsius."
    },
    {
        "keywords": ["pusing", "sakit kepala", "migrain", "nyeri kepala", "kepala berat"],
        "conditions": [
            {
                "nama_kondisi": "Sakit Kepala Tegang",
                "nama_kondisi_medis": "Tension Headache",
                "kode_icd10": "G44.2",
                "probabilitas": "tinggi",
                "penjelasan": "Nyeri kepala akibat ketegangan otot di sekitar leher dan kulit kepala, sering dipicu stres atau kurang tidur.",
                "saran_tindakan": "Istirahat di ruangan tenang, pijat leher secara perlahan, atau konsumsi ibuprofen/parasetamol.",
            },
            {
                "nama_kondisi": "Dehidrasi",
                "nama_kondisi_medis": "Dehydration / Volume Depletion",
                "kode_icd10": "E86",
                "probabilitas": "sedang",
                "penjelasan": "Kurangnya asupan cairan tubuh yang mengganggu keseimbangan elektrolit dan fungsi normal organ.",
                "saran_tindakan": "Minum air putih secara perlahan dalam jumlah banyak atau larutan elektrolit oralit.",
            }
        ],
        "urgensi": "rendah",
        "saran_umum": "Kurangi waktu layar (screen time), istirahatkan mata Anda, dan pastikan Anda terhidrasi dengan baik."
    },
    {
        "keywords": ["mual", "muntah", "sakit perut", "nyeri lambung", "maag", "kembung", "perih perut"],
        "conditions": [
            {
                "nama_kondisi": "Dispepsia / Sakit Maag",
                "nama_kondisi_medis": "Dyspepsia / Gastritis",
                "kode_icd10": "K30",
                "probabilitas": "tinggi",
                "penjelasan": "Gangguan pencernaan akibat peningkatan asam lambung atau iritasi pada dinding lambung.",
                "saran_tindakan": "Makan dalam porsi kecil tapi sering, hindari makanan pedas dan asam, konsumsi antasida jika diperlukan.",
            },
            {
                "nama_kondisi": "Gastroenteritis (Flu Perut)",
                "nama_kondisi_medis": "Gastroenteritis / Stomach Flu",
                "kode_icd10": "A09",
                "probabilitas": "sedang",
                "penjelasan": "Peradangan lambung dan usus akibat infeksi bakteri atau virus, sering ditandai diare dan muntah.",
                "saran_tindakan": "Minum oralit untuk mencegah dehidrasi akibat cairan yang keluar lewat diare/muntah.",
            }
        ],
        "urgensi": "sedang",
        "saran_umum": "Hindari konsumsi kopi, susu, makanan berserat tinggi, pedas, dan berlemak untuk sementara waktu hingga lambung pulih."
    },
    {
        "keywords": ["batuk", "pilek", "hidung tersumbat", "bersin", "tenggorokan gatal", "nyeri tenggorokan"],
        "conditions": [
            {
                "nama_kondisi": "Common Cold (Flu Ringan)",
                "nama_kondisi_medis": "Nasopharyngitis / Cold",
                "kode_icd10": "J00",
                "probabilitas": "tinggi",
                "penjelasan": "Infeksi virus ringan pada saluran hidung dan tenggorokan.",
                "saran_tindakan": "Konsumsi air hangat dengan madu/lemon, hisap tablet pelega tenggorokan, dan istirahat yang cukup.",
            },
            {
                "nama_kondisi": "Faringitis Akut (Radang Tenggorokan)",
                "nama_kondisi_medis": "Acute Pharyngitis",
                "kode_icd10": "J02.9",
                "probabilitas": "sedang",
                "penjelasan": "Peradangan pada mukosa tenggorokan yang menyebabkan nyeri saat menelan.",
                "saran_tindakan": "Kumur dengan air garam hangat, hindari makanan gorengan/berminyak, minum obat pereda nyeri tenggorokan.",
            }
        ],
        "urgensi": "rendah",
        "saran_umum": "Konsumsi makanan bernutrisi tinggi dan vitamin C. Gunakan masker saat berinteraksi agar tidak menularkan ke orang lain."
    }
]


def check_symptoms(request: SymptomCheckRequest) -> SymptomCheckResponse:
    """Menganalisis daftar gejala dan mengembalikan kesimpulan analisis."""
    
    gejala_input = [g.lower().strip() for g in request.gejala]
    gejala_dianalisis = []
    gejala_tidak_dikenal = []
    kondisi_mungkin = []
    
    tingkat_urgensi = "rendah"
    saran_umum = "Istirahatlah yang cukup dan pantau kondisi Anda. Hubungi dokter umum di aplikasi JagaDiri jika gejala berlanjut lebih dari 3 hari."
    
    # Deteksi kecocokan aturan
    matched_conditions = []
    urgency_scores = {"rendah": 1, "sedang": 2, "tinggi": 3, "darurat": 4}
    max_urgency_score = 1
    
    for rule in RULES:
        match_found = False
        for kw in rule["keywords"]:
            for gj in gejala_input:
                if kw in gj or gj in kw:
                    match_found = True
                    if gj not in gejala_dianalisis:
                        gejala_dianalisis.append(gj)
        
        if match_found:
            for cond in rule["conditions"]:
                kondisi_mungkin.append(
                    PossibleCondition(
                        nama_kondisi=cond["nama_kondisi"],
                        nama_kondisi_medis=cond["nama_kondisi_medis"],
                        kode_icd10=cond["kode_icd10"],
                        probabilitas=cond["probabilitas"],
                        penjelasan=cond["penjelasan"],
                        saran_tindakan=cond["saran_tindakan"],
                    )
                )
            
            # Update urgensi tertinggi
            rule_urgency = rule["urgensi"]
            if urgency_scores[rule_urgency] > max_urgency_score:
                max_urgency_score = urgency_scores[rule_urgency]
                tingkat_urgensi = rule_urgency
                saran_umum = rule["saran_umum"]

    # Identifikasi gejala yang tidak dikenal
    for gj in gejala_input:
        if gj not in gejala_dianalisis:
            gejala_tidak_dikenal.append(gj)
            
    # Jika tidak ada aturan yang cocok, berikan fallback default
    if not kondisi_mungkin:
        kondisi_mungkin.append(
            PossibleCondition(
                nama_kondisi="Kelelahan Fisik / Kurang Istirahat",
                nama_kondisi_medis="Fatigue / Malaise",
                kode_icd10="R53.83",
                probabilitas="tinggi",
                penjelasan="Kondisi lemas dan lelah akibat kurang tidur, aktivitas berlebih, atau stres psikologis.",
                saran_tindakan="Tidur 7-8 jam per hari, konsumsi makanan sehat, kurangi konsumsi kafein berlebih.",
            )
        )
        
    return SymptomCheckResponse(
        gejala_dianalisis=gejala_dianalisis if gejala_dianalisis else ["Kondisi umum"],
        gejala_tidak_dikenal=gejala_tidak_dikenal,
        kondisi_mungkin=kondisi_mungkin,
        tingkat_urgensi=tingkat_urgensi,
        saran_umum=saran_umum,
    )

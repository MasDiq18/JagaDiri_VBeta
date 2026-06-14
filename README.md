# 🛡️ JagaDiri — Platform Kesehatan Digital Indonesia

> **"Selalu Ada yang Jaga"** — Jaring pengaman kesehatan digital untuk mereka yang hidup sendiri.

![JagaDiri](https://img.shields.io/badge/Status-MVP%20Development-brightgreen)
![License](https://img.shields.io/badge/License-Proprietary-blue)
![Indonesia](https://img.shields.io/badge/🇮🇩-Made%20in%20Indonesia-red)

## 📋 Tentang JagaDiri

JagaDiri adalah platform kesehatan digital yang dirancang khusus untuk individu yang hidup sendiri (*solo living*) di Indonesia. Platform ini berfungsi sebagai **jaring pengaman kesehatan digital** yang melindungi pengguna secara proaktif — bahkan sebelum mereka meminta bantuan.

### Target Pengguna
- 🏠 Pekerja muda urban yang tinggal sendiri
- 👴 Lansia yang tinggal mandiri
- 🎓 Mahasiswa perantau
- 💼 Profesional dengan kondisi kronis
- 🤰 Perempuan yang menjalani kehamilan tanpa pendampingan
- 🌍 Pekerja migran di kota besar

## 🏗️ Arsitektur

```mermaid
graph TB
    subgraph Frontend
        WEB[Next.js 14 Web App]
        MOBILE[React Native Mobile - TBD]
    end
    
    subgraph Backend
        API[FastAPI - API Utama]
        RT[Socket.io - Real-time - TBD]
        AI[AI/ML Service - TBD]
        WORKER[Celery Workers - TBD]
    end
    
    subgraph Database
        PG[(PostgreSQL 16)]
        RD[(Redis 7)]
    end
    
    WEB --> API
    MOBILE --> API
    API --> PG
    API --> RD
    
    style WEB fill:#1A6B5A,color:white
    style API fill:#2B5EA7,color:white
    style PG fill:#336791,color:white
    style RD fill:#DC382D,color:white
```

## 🚀 Memulai

### Prasyarat
- Docker & Docker Compose
- Node.js 20+ (untuk development frontend)
- Python 3.12+ (untuk development backend)

### Setup Cepat (Docker Compose)

```bash
# 1. Clone repositori
git clone https://github.com/jagadiri/jagadiri.git
cd jagadiri

# 2. Salin environment variables
cp .env.example .env

# 3. Jalankan semua layanan
docker compose up --build

# 4. Buka di browser
# Web App   : http://localhost:3000
# API Docs  : http://localhost:8000/docs
# API Health: http://localhost:8000/health
```

### Development Lokal (Tanpa Docker)

```bash
# Backend
cd services/api
python -m venv venv
source venv/bin/activate  # atau venv\Scripts\activate di Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd apps/web
npm install
npm run dev
```

## 📚 Fitur Utama

| Fitur | Deskripsi | Status |
|-------|-----------|--------|
| 🔔 **SafePing** | Check-in kesehatan harian dengan eskalasi otomatis | ✅ MVP |
| 🆘 **SOS Darurat** | Tombol panik dengan notifikasi GPS ke kontak darurat | ✅ MVP |
| 👨‍⚕️ **Konsultasi Online** | Chat dan video call dengan dokter (Agora SDK) | ✅ MVP (chat) |
| 💊 **MedReminder** | Pengingat obat cerdas dengan tracking kepatuhan | ✅ MVP |
| 🪪 **MedCard** | Kartu medis darurat digital via QR Code | ✅ MVP |
| 🤖 **AI Symptom Checker** | Pengecekan gejala berbasis aturan dengan triase | ✅ MVP |
| 👨‍👩‍👧‍👦 **Portal Keluarga** | Dashboard monitoring untuk keluarga/caregiver | ✅ MVP |
| 📊 **PHR** | Personal Health Records & vital signs tracking | ✅ MVP |
| 🏆 **Gamifikasi** | Poin, streak, dan health goals | 🔜 Fase 2 |
| 🧠 **Kesehatan Mental** | Mood journal, CBT tools | 🔜 Fase 2 |
| ⌚ **Wearable** | Integrasi Apple Health & Google Fit | 🔜 Fase 2 |
| 🏢 **Korporat** | Dashboard HR B2B | 🔜 Fase 3 |

## 🔐 Keamanan & Kepatuhan

- ✅ JWT authentication dengan refresh token rotation
- ✅ Enkripsi data medis (AES-256)
- ✅ Rate limiting per endpoint
- ✅ Audit log untuk semua akses data medis
- ✅ Kepatuhan UU PDP (data di server Indonesia)
- ✅ WCAG AA accessibility compliance

## 📁 Struktur Proyek

```
jagadiri/
├── apps/web/                  # Next.js 14 Frontend
├── services/api/              # FastAPI Backend
├── database/                  # Migrations & Seeds
├── shared/                    # Shared types & constants
└── docker-compose.yml
```

## 🤝 Kontribusi

Lihat [CONTRIBUTING.md](CONTRIBUTING.md) untuk panduan kontribusi.

## 📝 Lisensi

Hak cipta dilindungi. Lihat [LICENSE](LICENSE) untuk detail.

---

**Motto Engineering:** *"Bangun seolah nyawa seseorang bergantung padanya — karena mungkin memang begitu."*

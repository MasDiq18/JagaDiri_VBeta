"""
JagaDiri — Konfigurasi Aplikasi
Menggunakan pydantic-settings untuk memuat variabel environment.
"""

import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    """Pengaturan aplikasi yang dimuat dari environment variables."""

    # === App ===
    APP_NAME: str = "JagaDiri API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True

    # === Database ===
    # Wajib diisi di .env — jangan hardcode connection string di sini.
    # Format Supabase Session Pooler:
    #   postgresql+asyncpg://postgres.xxxxx:PASSWORD@aws-0-region.pooler.supabase.com:5432/postgres?ssl=require
    DATABASE_URL: str = ""

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "\n\n[KONFIGURASI] DATABASE_URL belum diatur!\n"
                "Salin file .env.example menjadi .env dan isi dengan connection string Supabase.\n"
                "Contoh:\n"
                "  DATABASE_URL=\"postgresql+asyncpg://postgres.xxxxx:PASSWORD@aws-0-region.pooler.supabase.com:5432/postgres?ssl=require\"\n"
            )
        return v.strip()

    # === Redis (opsional — fallback in-memory tersedia) ===
    REDIS_URL: str = ""

    # === Auth / JWT ===
    JWT_SECRET_KEY: str = "jagadiri-dev-secret-key-change-in-production-2024"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # === CORS ===
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # === Enkripsi Data Medis ===
    ENCRYPTION_KEY: str = "0123456789abcdef0123456789abcdef"

    # === Third Party (opsional untuk MVP) ===
    AGORA_APP_ID: str = ""
    AGORA_APP_CERTIFICATE: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    GOOGLE_MAPS_API_KEY: str = ""

    # === Storage ===
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_MEDICAL_FILES: str = "jagadiri-medical"
    MINIO_BUCKET_PROFILE_PHOTOS: str = "jagadiri-profiles"

    # === Email ===
    ADMIN_EMAIL: str = "admin@jagadiri.id"
    SUPPORT_EMAIL: str = "support@jagadiri.id"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()

"""
JagaDiri — Database Setup
SQLAlchemy 2.0 async engine dan session factory.
Koneksi database dibaca dari environment variable DATABASE_URL.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

from sqlalchemy import MetaData, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from app.core.config import settings

logger = logging.getLogger("jagadiri.database")

# Naming convention untuk constraint (agar migration konsisten)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

# ─────────────────────────────────────────────
# Deteksi apakah koneksi ke Supabase (atau remote)
# Jika URL mengandung 'supabase' atau BUKAN localhost, aktifkan SSL.
# ─────────────────────────────────────────────
_db_url = settings.DATABASE_URL
_is_remote = (
    "supabase" in _db_url
    or "pooler" in _db_url
    or "localhost" not in _db_url
    and "127.0.0.1" not in _db_url
)

# connect_args untuk asyncpg:
# - ssl="require" wajib untuk Supabase
# - server_settings: statement_timeout sebagai jaring pengaman
_connect_args: dict = {}
if _is_remote:
    _connect_args["ssl"] = "require"
    logger.info("Database: koneksi SSL aktif (remote/Supabase).")
else:
    logger.info("Database: koneksi tanpa SSL (localhost).")

# Async engine
engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    pool_size=5,          # Lebih konservatif untuk Supabase free tier
    max_overflow=10,
    pool_pre_ping=True,   # Cek koneksi sebelum digunakan (penting untuk idle timeout)
    pool_recycle=300,     # Recycle koneksi tiap 5 menit (hindari timeout Supabase)
    connect_args=_connect_args,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class untuk semua model SQLAlchemy."""

    metadata = metadata

    # Kolom bersama untuk semua tabel
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # TIMESTAMP WITH TIME ZONE — konsisten dengan asyncpg
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # TIMESTAMP WITH TIME ZONE — konsisten dengan asyncpg
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection untuk database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Buat semua tabel (untuk development). Gunakan Alembic di produksi."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Hapus semua tabel (untuk testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

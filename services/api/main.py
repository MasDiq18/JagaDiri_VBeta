"""
JagaDiri — FastAPI Backend Entry Point
Mengonfigurasi server web, middleware, routing, dan inisialisasi database.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables, async_session_factory
from app.middleware.audit_log import AuditLogMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.seeds.seed_data import seed_all_data

# Konfigurasi logging dasar
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("jagadiri.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan untuk inisialisasi tabel database dan data seeding saat server dimulai."""
    logger.info("Memulai inisialisasi JagaDiri API...")
    try:
        # Inisialisasi tabel database
        await create_tables()
        logger.info("Tabel database berhasil diinisialisasi.")
        
        # Jalankan data seeding
        async with async_session_factory() as session:
            await seed_all_data(session)
            await session.commit()
            
    except Exception as e:
        logger.error("Gagal melakukan inisialisasi startup: %s", e)
        
    yield
    logger.info("JagaDiri API dimatikan.")


# Setup FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API untuk JagaDiri — Jaring pengaman kesehatan digital solo living.",
    lifespan=lifespan,
)

# === 1. CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 2. Custom Middlewares ===
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditLogMiddleware)

# === 3. Register Routers ===
from app.routers import (
    auth,
    users,
    safeguard,
    consultations,
    medications,
    health_records,
    family,
    ai,
)

app.include_router(auth.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(safeguard.router, prefix="/v1")
app.include_router(consultations.router, prefix="/v1")
app.include_router(medications.router, prefix="/v1")
app.include_router(health_records.router, prefix="/v1")
app.include_router(family.router, prefix="/v1")
app.include_router(ai.router, prefix="/v1")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint root untuk memeriksa status kesehatan API."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@app.get("/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint termasuk status koneksi database."""
    from app.core.database import engine
    from sqlalchemy import text
    db_status = "disconnected"
    db_latency_ms = None
    try:
        import time
        start = time.time()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - start) * 1000, 1)
        db_status = "connected"
    except Exception as e:
        logger.warning("Database health check gagal: %s", e)
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "database_latency_ms": db_latency_ms,
        "app_version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }

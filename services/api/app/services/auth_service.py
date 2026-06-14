"""
JagaDiri — Layanan Autentikasi
Business logic untuk registrasi, login, JWT management, OTP, dan reset password.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.safeping import SafePingConfig
from app.models.user import RefreshToken, User, UserMedicalProfile
from app.schemas.auth import (
    LoginResponse,
    RegisterRequest,
    TokenResponse,
    UserBriefResponse,
)
from app.services.notification_service import notification_service

logger = logging.getLogger("jagadiri.auth")

# In-memory OTP store (gunakan Redis di produksi)
_otp_store: dict[str, dict] = {}


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    """Daftarkan pengguna baru."""

    # Cek apakah email sudah digunakan
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email sudah terdaftar. Silakan gunakan email lain atau login.",
        )

    # Cek apakah nomor telepon sudah digunakan
    if data.phone:
        existing_phone = await db.execute(select(User).where(User.phone == data.phone))
        if existing_phone.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Nomor telepon sudah terdaftar.",
            )

    # Buat user baru
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
    )
    db.add(user)
    await db.flush()

    # Buat profil medis kosong
    medical_profile = UserMedicalProfile(user_id=user.id)
    db.add(medical_profile)

    # Buat konfigurasi SafePing default
    safeping_config = SafePingConfig(user_id=user.id)
    db.add(safeping_config)

    await db.flush()
    await db.refresh(user)

    logger.info("Pengguna baru terdaftar: %s (%s)", user.full_name, user.email)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> LoginResponse:
    """Autentikasi pengguna dan kembalikan token."""

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau kata sandi salah.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun Anda telah dinonaktifkan. Hubungi dukungan untuk bantuan.",
        )

    # Buat token
    access_token = create_access_token(user.id, role="patient")
    refresh_token = create_refresh_token(user.id)

    # Simpan refresh token di database
    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(token_record)
    await db.flush()

    logger.info("Login berhasil: %s", user.email)

    return LoginResponse(
        pesan="Login berhasil",
        token=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
        user=UserBriefResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified,
            subscription_tier=user.subscription_tier,
        ),
    )


async def refresh_access_token(db: AsyncSession, refresh_token_str: str) -> TokenResponse:
    """Perbarui access token menggunakan refresh token."""

    payload = decode_token(refresh_token_str)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token tidak valid atau sudah kadaluarsa.",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak mengandung identitas pengguna.",
        )

    # Verifikasi token masih aktif di database
    token_hash = hash_token(refresh_token_str)
    result = await db.execute(
        select(RefreshToken).where(
            and_(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
    )
    stored_token = result.scalar_one_or_none()

    if stored_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token sudah dicabut atau kadaluarsa.",
        )

    # Verifikasi user masih aktif
    user_result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = user_result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pengguna tidak ditemukan atau sudah dinonaktifkan.",
        )

    # Buat access token baru
    new_access_token = create_access_token(user.id, role="patient")

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def logout_user(
    db: AsyncSession,
    user_id: UUID,
    refresh_token_str: Optional[str] = None,
) -> None:
    """Logout pengguna dan cabut refresh token."""

    if refresh_token_str:
        token_hash = hash_token(refresh_token_str)
        result = await db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.user_id == user_id,
                )
            )
        )
        token = result.scalar_one_or_none()
        if token:
            token.revoked_at = datetime.now(timezone.utc)
            await db.flush()

    logger.info("Logout berhasil: user_id=%s", user_id)


async def forgot_password(db: AsyncSession, email: str) -> str:
    """Kirim OTP untuk reset password."""

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Selalu kembalikan pesan sukses (keamanan)
    if user is None:
        logger.warning("Permintaan reset password untuk email tidak terdaftar: %s", email)
        return "Jika email terdaftar, kode OTP akan dikirim ke email Anda."

    # Generate dan simpan OTP
    otp_code = generate_otp()
    _otp_store[email] = {
        "code": otp_code,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
        "verified": False,
    }

    # Kirim OTP (mock)
    await notification_service.send_otp(email, otp_code)

    logger.info("OTP dikirim ke: %s", email)
    return "Jika email terdaftar, kode OTP akan dikirim ke email Anda."


async def verify_otp(email: str, otp_code: str) -> bool:
    """Verifikasi kode OTP."""

    stored = _otp_store.get(email)
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP tidak ditemukan. Silakan minta kode baru.",
        )

    if datetime.now(timezone.utc) > stored["expires_at"]:
        _otp_store.pop(email, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP sudah kadaluarsa. Silakan minta kode baru.",
        )

    if stored["code"] != otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP tidak valid.",
        )

    stored["verified"] = True
    return True


async def reset_password(
    db: AsyncSession, email: str, otp_code: str, new_password: str
) -> None:
    """Reset password setelah verifikasi OTP."""

    stored = _otp_store.get(email)
    if stored is None or not stored.get("verified") or stored["code"] != otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP tidak valid atau belum diverifikasi. Verifikasi OTP terlebih dahulu.",
        )

    if datetime.now(timezone.utc) > stored["expires_at"]:
        _otp_store.pop(email, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode OTP sudah kadaluarsa.",
        )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan.",
        )

    user.password_hash = hash_password(new_password)
    await db.flush()

    # Hapus OTP setelah digunakan
    _otp_store.pop(email, None)

    # Cabut semua refresh token
    result = await db.execute(
        select(RefreshToken).where(
            and_(
                RefreshToken.user_id == user.id,
                RefreshToken.revoked_at.is_(None),
            )
        )
    )
    tokens = result.scalars().all()
    for token in tokens:
        token.revoked_at = datetime.now(timezone.utc)

    await db.flush()
    logger.info("Password berhasil direset: %s", email)

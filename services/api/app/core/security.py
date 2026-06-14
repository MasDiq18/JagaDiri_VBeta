"""
JagaDiri — Keamanan & Autentikasi
JWT tokens, password hashing, dan enkripsi data sensitif.
"""

import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# === Password Hashing ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password terhadap hash."""
    return pwd_context.verify(plain_password, hashed_password)


# === JWT Token ===
def create_access_token(
    user_id: UUID,
    role: str = "patient",
    extra_claims: Optional[dict] = None,
) -> str:
    """Buat access token JWT (TTL: 15 menit default)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """Buat refresh token JWT (TTL: 7 hari default)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32),  # Unique token ID untuk revocation
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode dan verifikasi JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """Hash token untuk penyimpanan di database (refresh tokens)."""
    return hashlib.sha256(token.encode()).hexdigest()


# === OTP ===
def generate_otp(length: int = 6) -> str:
    """Generate OTP numerik."""
    return "".join([str(secrets.randbelow(10)) for _ in range(length)])


# === Enkripsi Field-Level (AES-256 simplified untuk MVP) ===
# Untuk produksi, gunakan library cryptography dengan Fernet
def encrypt_sensitive_field(value: str) -> str:
    """Enkripsi data sensitif. MVP: simple XOR + base64. Ganti dengan AES-256 di produksi."""
    # TODO: Implementasi AES-256-GCM untuk produksi
    key = settings.ENCRYPTION_KEY.encode()[:32]
    encrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(value.encode())])
    return base64.b64encode(encrypted).decode()


def decrypt_sensitive_field(encrypted_value: str) -> str:
    """Dekripsi data sensitif."""
    key = settings.ENCRYPTION_KEY.encode()[:32]
    decoded = base64.b64decode(encrypted_value.encode())
    decrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(decoded)])
    return decrypted.decode()

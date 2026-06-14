"""
JagaDiri — Schema Autentikasi
Schemas untuk registrasi, login, token, OTP, dan reset password.
"""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """Permintaan registrasi pengguna baru."""

    email: EmailStr = Field(..., description="Alamat email pengguna")
    password: str = Field(
        ..., min_length=8, max_length=128,
        description="Kata sandi minimal 8 karakter, harus mengandung huruf besar, kecil, dan angka",
    )
    full_name: str = Field(
        ..., min_length=2, max_length=255,
        description="Nama lengkap pengguna",
    )
    phone: Optional[str] = Field(
        None, max_length=20,
        description="Nomor telepon (format: +62xxx)",
    )
    date_of_birth: Optional[date] = Field(None, description="Tanggal lahir (YYYY-MM-DD)")
    gender: Optional[str] = Field(None, description="Jenis kelamin: male, female, other")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Kata sandi harus mengandung minimal satu huruf besar")
        if not re.search(r"[a-z]", v):
            raise ValueError("Kata sandi harus mengandung minimal satu huruf kecil")
        if not re.search(r"[0-9]", v):
            raise ValueError("Kata sandi harus mengandung minimal satu angka")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("male", "female", "other"):
            raise ValueError("Jenis kelamin harus salah satu dari: male, female, other")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^\+?[0-9]{8,15}$", v):
            raise ValueError("Format nomor telepon tidak valid")
        return v


class LoginRequest(BaseModel):
    """Permintaan login."""

    email: EmailStr = Field(..., description="Alamat email")
    password: str = Field(..., description="Kata sandi")


class TokenResponse(BaseModel):
    """Respons token JWT."""

    access_token: str = Field(..., description="Token akses JWT")
    refresh_token: str = Field(..., description="Token refresh JWT")
    token_type: str = Field(default="bearer", description="Tipe token")
    expires_in: int = Field(..., description="Masa berlaku access token dalam detik")


class LoginResponse(BaseModel):
    """Respons login berhasil."""

    pesan: str = Field(default="Login berhasil", description="Pesan sukses")
    token: TokenResponse
    user: "UserBriefResponse"


class UserBriefResponse(BaseModel):
    """Ringkasan data pengguna untuk login response."""

    id: UUID
    email: str
    full_name: str
    is_verified: bool
    subscription_tier: str

    model_config = ConfigDict(from_attributes=True)


class RefreshRequest(BaseModel):
    """Permintaan refresh token."""

    refresh_token: str = Field(..., description="Token refresh yang masih berlaku")


class LogoutRequest(BaseModel):
    """Permintaan logout."""

    refresh_token: Optional[str] = Field(None, description="Token refresh untuk dicabut")


class ForgotPasswordRequest(BaseModel):
    """Permintaan lupa kata sandi."""

    email: EmailStr = Field(..., description="Email yang terdaftar")


class VerifyOTPRequest(BaseModel):
    """Verifikasi kode OTP."""

    email: EmailStr = Field(..., description="Email pengguna")
    otp_code: str = Field(
        ..., min_length=6, max_length=6,
        description="Kode OTP 6 digit",
    )


class ResetPasswordRequest(BaseModel):
    """Reset kata sandi menggunakan OTP."""

    email: EmailStr = Field(..., description="Email pengguna")
    otp_code: str = Field(..., min_length=6, max_length=6, description="Kode OTP 6 digit")
    new_password: str = Field(
        ..., min_length=8, max_length=128,
        description="Kata sandi baru",
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Kata sandi harus mengandung minimal satu huruf besar")
        if not re.search(r"[a-z]", v):
            raise ValueError("Kata sandi harus mengandung minimal satu huruf kecil")
        if not re.search(r"[0-9]", v):
            raise ValueError("Kata sandi harus mengandung minimal satu angka")
        return v


# Update forward reference
LoginResponse.model_rebuild()

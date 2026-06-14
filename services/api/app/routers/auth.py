"""
JagaDiri — Router Autentikasi
Endpoints untuk registrasi, login, refresh token, OTP, dan reset password.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    LoginResponse,
    RefreshRequest,
    LogoutRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
)
from app.schemas.user import UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autentikasi"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrasi pengguna baru",
)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Mendaftarkan pengguna baru ke platform JagaDiri."""
    return await auth_service.register_user(db, data)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login pengguna",
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Melakukan login dan mengembalikan token akses JWT."""
    return await auth_service.login_user(db, data.email, data.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Perbarui token akses",
)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Memperbarui token akses (access token) menggunakan refresh token."""
    return await auth_service.refresh_access_token(db, data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout pengguna",
)
async def logout(
    data: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mencabut session token saat ini dan logout."""
    await auth_service.logout_user(db, current_user.id, data.refresh_token)
    return {"pesan": "Logout berhasil"}


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Lupa kata sandi (Minta OTP)",
)
async def forgot_pwd(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Mengirimkan kode OTP ke email pengguna yang terdaftar untuk keperluan reset kata sandi."""
    pesan = await auth_service.forgot_password(db, data.email)
    return {"pesan": pesan}


@router.post(
    "/verify-otp",
    status_code=status.HTTP_200_OK,
    summary="Verifikasi kode OTP",
)
async def verify(data: VerifyOTPRequest):
    """Memverifikasi kecocokan kode OTP yang dikirimkan ke email."""
    await auth_service.verify_otp(data.email, data.otp_code)
    return {"pesan": "Kode OTP berhasil diverifikasi"}


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset kata sandi",
)
async def reset_pwd(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Mengubah kata sandi pengguna ke kata sandi baru setelah OTP sukses diverifikasi."""
    await auth_service.reset_password(db, data.email, data.otp_code, data.new_password)
    return {"pesan": "Kata sandi berhasil diubah"}

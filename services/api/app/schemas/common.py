"""
JagaDiri — Schema Umum
Schemas yang digunakan di seluruh API.
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Respons pesan sederhana."""

    pesan: str = Field(..., description="Pesan respons")


class ErrorResponse(BaseModel):
    """Respons error standar."""

    detail: str = Field(..., description="Deskripsi error")
    kode_error: Optional[str] = Field(None, description="Kode error internal")


class PaginatedResponse(BaseModel, Generic[T]):
    """Respons dengan paginasi."""

    data: List[T] = Field(default_factory=list, description="Daftar item")
    total: int = Field(..., description="Total seluruh data")
    halaman: int = Field(..., description="Halaman saat ini")
    per_halaman: int = Field(..., description="Jumlah item per halaman")
    total_halaman: int = Field(..., description="Total halaman tersedia")

    model_config = ConfigDict(from_attributes=True)


class HealthCheckResponse(BaseModel):
    """Respons health check."""

    status: str = "sehat"
    versi: str
    waktu: datetime
    database: str = "terhubung"

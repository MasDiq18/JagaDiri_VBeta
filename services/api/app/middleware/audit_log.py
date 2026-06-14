"""
JagaDiri — Audit Log Middleware
Mencatat akses ke data medis sensitif (siapa, kapan, apa yang diakses).
"""

import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("jagadiri.audit")


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Proses request
        response = await call_next(request)
        
        duration = time.time() - start_time
        path = request.url.path
        method = request.method
        
        # Catat akses ke endpoint rekam medis, medcard, dan rekam obat sensitif
        if any(keyword in path for keyword in ["medical", "medcard", "health-records", "medications"]):
            status_code = response.status_code
            # Di produksi, ambil user_id dari JWT token yang ada di header
            auth_header = request.headers.get("Authorization")
            user_info = "Guest/Unauthenticated"
            if auth_header and auth_header.startswith("Bearer "):
                user_info = "Authenticated User" # Di produksi: decode token untuk dapatkan user_id

            logger.info(
                "AUDIT LOG: [Method=%s] [Path=%s] [User=%s] [Status=%s] [Duration=%.4fs]",
                method, path, user_info, status_code, duration
            )
            
        return response

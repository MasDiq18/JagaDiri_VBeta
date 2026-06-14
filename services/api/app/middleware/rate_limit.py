"""
JagaDiri — Rate Limiting Middleware
Membatasi jumlah request per menit untuk menjaga kestabilan server (in-memory fallback untuk MVP).
"""

import time
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Struktur data sederhana untuk menyimpan timestamp request per IP klien
        self.request_history = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Bersihkan riwayat lama (> 60 detik yang lalu)
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []
            
        self.request_history[client_ip] = [
            t for t in self.request_history[client_ip] if now - t < 60
        ]
        
        # Hapus entry IP yang sudah tidak punya riwayat untuk mencegah memory leak
        if not self.request_history[client_ip]:
            del self.request_history[client_ip]
            self.request_history[client_ip] = []
        
        # Atur batas: maks 100 request per menit untuk MVP
        limit = 100
        
        # Endpoint krusial seperti login/register/forgot-password memiliki limit lebih ketat
        path = request.url.path
        if any(keyword in path for keyword in ["/login", "/register", "/forgot-password"]):
            limit = 10  # 10 request per menit untuk auth sensitive
        elif "/sos" in path:
            limit = 5   # 5 request per menit untuk tombol darurat SOS

        if len(self.request_history[client_ip]) >= limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Terlalu banyak permintaan. Silakan tunggu satu menit sebelum mencoba kembali."
                },
            )
            
        self.request_history[client_ip].append(now)
        return await call_next(request)

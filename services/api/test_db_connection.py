"""
JagaDiri — Test Koneksi Database Supabase
==========================================
Script sederhana untuk memverifikasi koneksi ke Supabase PostgreSQL.
Jalankan sebelum menjalankan API untuk memastikan database terhubung.

Cara penggunaan:
    .venv\\Scripts\\python.exe test_db_connection.py

Pastikan file .env sudah ada di folder ini (services/api/) dan
DATABASE_URL sudah diisi dengan connection string Supabase.
"""

import asyncio
import os
import sys
import time

# ─── Muat .env ───────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅  .env berhasil dimuat.")
except ImportError:
    print("⚠️   python-dotenv tidak terinstall. Membaca env dari sistem...")

# ─── Cek DATABASE_URL ────────────────────────────────────────────────────────
database_url = os.getenv("DATABASE_URL", "").strip()

if not database_url:
    print("\n❌  ERROR: DATABASE_URL tidak ditemukan!")
    print("    Pastikan file .env ada di folder services/api/ dan berisi:")
    print('    DATABASE_URL="postgresql+asyncpg://postgres.xxxxx:PASSWORD@HOST:5432/postgres?ssl=require"')
    print("\n    Salin template:")
    print("      copy .env.example .env    (Windows)")
    print("      cp .env.example .env      (Linux/Mac)")
    sys.exit(1)


def mask_url(url: str) -> str:
    """Sembunyikan password dari connection string untuk logging."""
    try:
        import re
        return re.sub(r"(:)[^:@]+(@)", r"\1****\2", url)
    except Exception:
        return url[:40] + "..."


def print_troubleshoot(error_msg: str):
    """Tampilkan panduan troubleshoot berdasarkan jenis error."""
    print("\n🔧  PANDUAN TROUBLESHOOT:")
    error_lower = error_msg.lower()

    if "password" in error_lower or "authentication" in error_lower or "invalid password" in error_lower:
        print("    → Password salah. Periksa DATABASE_URL di file .env")
        print("    → Ganti password: Supabase Dashboard → Settings → Database → Reset password")

    elif "timeout" in error_lower or "connection refused" in error_lower or "could not connect" in error_lower:
        print("    → Tidak bisa terhubung ke server Supabase.")
        print("    → Periksa koneksi internet.")
        print("    → Pastikan project Supabase masih aktif di dashboard.")

    elif "ssl" in error_lower or "certificate" in error_lower:
        print("    → Masalah SSL. Pastikan DATABASE_URL mengandung '?ssl=require'")

    elif "host" in error_lower or "name or service not known" in error_lower or "nodename" in error_lower:
        print("    → Host tidak ditemukan. Periksa alamat Supabase di DATABASE_URL.")
        print("    → Pastikan project ref sudah benar (ganti 'xxxxx' dengan project ref Anda).")

    elif "ganti_" in error_lower or "your_password" in error_lower:
        print("    → DATABASE_URL masih berisi placeholder!")
        print("    → Edit file .env dan ganti GANTI_PROJECT_REF dan GANTI_PASSWORD")
        print("      dengan nilai asli dari Supabase Dashboard.")

    else:
        print("    → Cek ulang connection string DATABASE_URL di file .env")
        print("    → Format: postgresql+asyncpg://postgres.PROJECT_REF:PASSWORD@HOST:5432/postgres?ssl=require")

    print("\n    📖  Dokumentasi Supabase:")
    print("    https://supabase.com/docs/guides/database/connecting-to-postgres")


async def test_connection():
    """Test koneksi database menggunakan asyncpg."""
    import asyncpg

    # asyncpg menggunakan prefix "postgresql://" atau "postgres://"
    # Hapus prefix driver SQLAlchemy jika ada
    url = database_url
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("postgres+asyncpg://", "postgresql://")

    # Deteksi apakah butuh SSL (Supabase/remote)
    use_ssl = (
        "supabase" in url
        or "pooler" in url
        or ("localhost" not in url and "127.0.0.1" not in url)
    )

    print(f"🔗  Menghubungkan ke: {mask_url(url)}")
    if use_ssl:
        print("🔒  SSL: aktif (koneksi remote/Supabase)")
    else:
        print("🔓  SSL: nonaktif (localhost)")

    try:
        start = time.time()

        if use_ssl:
            import ssl as ssl_module
            ssl_ctx = ssl_module.create_default_context()
            # Supabase menggunakan sertifikat yang valid
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl_module.CERT_NONE
            # Hapus parameter ?ssl=require dari URL karena asyncpg menerima via ssl= kwarg
            clean_url = url.split("?")[0]
            conn = await asyncpg.connect(clean_url, ssl=ssl_ctx, timeout=15)
        else:
            clean_url = url.split("?")[0]
            conn = await asyncpg.connect(clean_url, timeout=15)

        # Jalankan query test
        row = await conn.fetchrow("SELECT NOW() AS server_time, version() AS pg_version;")
        latency_ms = round((time.time() - start) * 1000, 1)
        await conn.close()

        print(f"\n✅  KONEKSI BERHASIL! (latency: {latency_ms}ms)")
        print(f"    Server time : {row['server_time']}")
        print(f"    PostgreSQL  : {str(row['pg_version'])[:70]}...")
        return True

    except Exception as e:
        print(f"\n❌  KONEKSI GAGAL!")
        print(f"    Error: {e}")
        print_troubleshoot(str(e))
        return False


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  JagaDiri — Test Koneksi Database Supabase")
    print("=" * 60)

    # Cek placeholder belum diganti
    if "GANTI_PROJECT_REF" in database_url or "GANTI_PASSWORD" in database_url:
        print("\n⚠️   DATABASE_URL masih berisi placeholder!")
        print("    Edit file services/api/.env dan ganti:")
        print("    - GANTI_PROJECT_REF  → project ref Supabase Anda")
        print("    - GANTI_PASSWORD     → password database Supabase Anda")
        print("\n    Lihat cara mendapatkan connection string:")
        print("    Supabase Dashboard → Project → Settings → Database → Session pooler")
        print("=" * 60 + "\n")
        sys.exit(1)

    success = asyncio.run(test_connection())

    print("\n" + "=" * 60)
    if success:
        print("  ✅  Database siap digunakan!")
        print("\n  Jalankan API dengan perintah:")
        print("  .venv\\Scripts\\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("  ❌  Koneksi gagal. Perbaiki error di atas sebelum menjalankan API.")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)

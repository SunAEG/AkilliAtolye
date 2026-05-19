"""
Async migration runner.
migrations/ klasöründeki .sql dosyalarını sırasıyla çalıştırır.
Hangi migration'ların uygulandığı schema_migrations tablosunda takip edilir.
"""
import logging
import os
from pathlib import Path

import asyncpg

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def run_migrations(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        # Migrasyon takip tablosunu oluştur (yoksa)
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id         BIGSERIAL PRIMARY KEY,
                filename   TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )

        # Daha önce uygulanan migrasyonları al
        applied = {
            row["filename"]
            for row in await conn.fetch("SELECT filename FROM schema_migrations")
        }

        # SQL dosyalarını sırayla bul
        sql_files = sorted(
            f for f in MIGRATIONS_DIR.glob("*.sql")
            if f.name not in applied
        )

        if not sql_files:
            logger.info("✅ Tüm migration'lar zaten uygulanmış.")
            return

        for sql_file in sql_files:
            logger.info(f"⚙️  Migration uygulanıyor: {sql_file.name}")
            sql = sql_file.read_text(encoding="utf-8")

            try:
                # Tüm migration'ı tek transaction içinde çalıştır
                async with conn.transaction():
                    await conn.execute(sql)
                    await conn.execute(
                        "INSERT INTO schema_migrations (filename) VALUES ($1)",
                        sql_file.name,
                    )
                logger.info(f"✅ {sql_file.name} başarıyla uygulandı.")
            except Exception as exc:
                logger.error(f"❌ {sql_file.name} uygulanırken hata: {exc}")
                raise

async def main() -> None:
    import asyncio
    from app.core.database import create_pool, close_pool

    # Log formatını ayarla ki terminalde daha temiz okunsun
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    logger.info("⏳ Veritabanı bağlantısı kuruluyor...")
    pool = await create_pool()
    try:
        await run_migrations(pool)
        logger.info("🎉 Tüm işlemler başarıyla tamamlandı.")
    finally:
        await close_pool()
        logger.info("🔌 Veritabanı bağlantısı kapatıldı.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

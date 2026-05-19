import asyncpg
import json
from asyncpg import Pool
from app.core.config import get_settings

settings = get_settings()

# Uygulama genelinde tek bir connection pool
_pool: Pool | None = None


async def create_pool() -> Pool:
    """
    asyncpg connection pool'u oluşturur.
    Uygulama başlangıcında (lifespan) çağrılır.
    """
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.postgres_dsn,
        min_size=2,
        max_size=10,
        # JSONB alanlarını Python dict'e otomatik dönüştürmek için codec
        init=_register_jsonb_codec,
    )
    return _pool


async def close_pool() -> None:
    """
    Connection pool'u kapatır.
    Uygulama kapanışında (lifespan) çağrılır.
    """
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_pool() -> Pool:
    """Mevcut pool'u döndürür. Pool yoksa hata fırlatır."""
    if _pool is None:
        raise RuntimeError(
            "PostgreSQL connection pool başlatılmamış. "
            "Uygulama lifespan'ı kontrol edin."
        )
    return _pool


async def _register_jsonb_codec(conn: asyncpg.Connection) -> None:
    """
    asyncpg için JSONB codec'i kaydeder.
    Python dict ↔ JSON string dönüşümünü otomatik yapar;
    manuel json.loads() çağrısına gerek kalmaz.
    """
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
        format="text",
    )

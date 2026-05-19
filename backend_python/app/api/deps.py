from typing import AsyncGenerator
import asyncpg
from redis.asyncio import Redis

from app.core.database import get_pool
from app.core.cache import get_redis_client


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    FastAPI dependency: Her istek için pool'dan bir connection alır,
    istek sonunda bağlantıyı pool'a geri bırakır.

    Kullanım:
        @router.get("/items")
        async def list_items(conn: asyncpg.Connection = Depends(get_db)):
            rows = await conn.fetch("SELECT * FROM items")
            ...
    """
    async with get_pool().acquire() as conn:
        yield conn


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    FastAPI dependency: Paylaşımlı Redis client'ı döndürür.

    Kullanım:
        @router.get("/cache-test")
        async def cache_test(redis: Redis = Depends(get_redis)):
            await redis.set("key", "value", ex=60)
            ...
    """
    yield get_redis_client()

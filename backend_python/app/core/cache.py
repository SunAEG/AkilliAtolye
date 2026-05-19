import redis.asyncio as aioredis
from redis.asyncio import Redis
from app.core.config import get_settings

settings = get_settings()

# Uygulama genelinde tek bir Redis client
_redis: Redis | None = None


async def create_redis_client() -> Redis:
    """
    Async Redis client'ı oluşturur.
    Uygulama başlangıcında (lifespan) çağrılır.
    """
    global _redis
    _redis = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,  # Yanıtları otomatik olarak str'e çevirir
        max_connections=20,
    )
    # Bağlantıyı doğrula
    await _redis.ping()
    return _redis


async def close_redis_client() -> None:
    """
    Redis client'ı kapatır.
    Uygulama kapanışında (lifespan) çağrılır.
    """
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def get_redis_client() -> Redis:
    """Mevcut Redis client'ı döndürür. Client yoksa hata fırlatır."""
    if _redis is None:
        raise RuntimeError(
            "Redis client başlatılmamış. "
            "Uygulama lifespan'ı kontrol edin."
        )
    return _redis

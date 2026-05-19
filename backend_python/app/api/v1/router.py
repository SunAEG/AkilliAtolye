import json
import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis

from app.api.deps import get_db, get_redis
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.supervisor import router as supervisor_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.files import router as files_router
from app.api.v1.roles import router as roles_router
from app.api.v1.screens import router as screens_router
from app.api.v1.logs import router as logs_router

router.include_router(auth_router)
router.include_router(supervisor_router)
router.include_router(users_router)
router.include_router(files_router)
router.include_router(roles_router)
router.include_router(screens_router)
router.include_router(logs_router)


@router.get("/health", summary="Sağlık Kontrolü")
async def health_check(
    conn: asyncpg.Connection = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    PostgreSQL ve Redis bağlantılarını test eder.
    Tüm servisler sağlıklıysa 200 döner.
    """
    # PostgreSQL kontrolü
    try:
        pg_version = await conn.fetchval("SELECT version()")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"PostgreSQL hatası: {e}")

    # Redis kontrolü
    try:
        redis_pong = await redis.ping()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis hatası: {e}")

    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "postgres": {"status": "connected", "info": pg_version},
            "redis": {"status": "connected" if redis_pong else "error"},
        },
    }


@router.get("/jsonb-demo", summary="JSONB Yazma / Okuma Demosu")
async def jsonb_demo(conn: asyncpg.Connection = Depends(get_db)):
    """
    PostgreSQL JSONB alanına veri yazar ve geri okur.
    'demo_jsonb' tablosunu otomatik oluşturur (henüz yoksa).
    """
    # Tabloyu oluştur (ilk çalışmada)
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS demo_jsonb (
            id   SERIAL PRIMARY KEY,
            data JSONB NOT NULL
        )
        """
    )

    payload = {"message": "Merhaba JSONB!", "tags": ["fastapi", "async", "postgresql"]}

    # JSONB alanına yaz
    row_id = await conn.fetchval(
        "INSERT INTO demo_jsonb (data) VALUES ($1) RETURNING id",
        json.dumps(payload),
    )

    # Geri oku
    row = await conn.fetchrow("SELECT * FROM demo_jsonb WHERE id = $1", row_id)

    return {"inserted_id": row_id, "data": json.loads(row["data"])}


@router.get("/cache-demo", summary="Redis Cache Demosu")
async def cache_demo(redis: Redis = Depends(get_redis)):
    """
    Redis'e bir değer yazar (TTL: 30 sn) ve hemen geri okur.
    """
    key = "demo:greeting"
    value = "Merhaba Redis!"

    await redis.set(key, value, ex=30)
    cached = await redis.get(key)
    ttl = await redis.ttl(key)

    return {"key": key, "value": cached, "ttl_seconds": ttl}

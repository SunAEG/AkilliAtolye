from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import create_pool, close_pool
from app.core.cache import create_redis_client, close_redis_client
from app.core.rabbitmq import connect_rabbitmq, close_rabbitmq
from app.api.v1.router import router as v1_router

# ---------------------------------------------------------------------------
# Loglama
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


# ---------------------------------------------------------------------------
# Lifespan: başlangıç ve kapatma işlemleri
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    - Uygulama başlarken: PostgreSQL pool ve Redis client oluşturulur.
    - Uygulama kapanırken: Tüm bağlantılar düzgünce kapatılır.
    """
    logger.info("🚀 Uygulama başlatılıyor...")

    # --- Başlangıç ---
    logger.info("PostgreSQL connection pool oluşturuluyor...")
    await create_pool()
    logger.info("✅ PostgreSQL bağlandı.")

    logger.info("Redis client oluşturuluyor...")
    await create_redis_client()
    logger.info("✅ Redis bağlandı.")

    logger.info("RabbitMQ bağlantısı oluşturuluyor...")
    await connect_rabbitmq()
    logger.info("✅ RabbitMQ bağlandı.")

    yield  # Uygulama bu noktada istekleri karşılar

    # --- Kapatma ---
    logger.info("🛑 Uygulama kapatılıyor...")
    await close_pool()
    logger.info("PostgreSQL pool kapatıldı.")
    await close_redis_client()
    logger.info("Redis client kapatıldı.")
    await close_rabbitmq()
    logger.info("RabbitMQ bağlantısı kapatıldı.")


# ---------------------------------------------------------------------------
# FastAPI uygulaması
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AkilliAtolye mikroservis backend'i. "
        "Async PostgreSQL (JSONB destekli) ve Redis bağlantısı hazır."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Router'ları dahil et
# ---------------------------------------------------------------------------
app.include_router(v1_router, prefix="/api/v1", tags=["v1"])


# ---------------------------------------------------------------------------
# Kök endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }

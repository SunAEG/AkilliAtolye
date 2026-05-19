import logging
import aio_pika
from aio_pika.patterns import RPC

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_rmq_connection: aio_pika.Connection | None = None
_rmq_channel: aio_pika.Channel | None = None
_rpc: RPC | None = None


async def connect_rabbitmq() -> None:
    """
    RabbitMQ bağlantısını, kanalını ve genel RPC nesnesini oluşturur.
    FastAPI lifespan'de çağrılır.
    """
    global _rmq_connection, _rmq_channel, _rpc

    try:
        _rmq_connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        _rmq_channel = await _rmq_connection.channel()
        
        # RPC pattern nesnesini oluştur
        _rpc = await RPC.create(_rmq_channel)
        
        logger.info("RabbitMQ RPC Client başarıyla başlatıldı.")
    except Exception as e:
        logger.error(f"RabbitMQ bağlantı hatası: {e}")
        raise


async def close_rabbitmq() -> None:
    """
    RabbitMQ bağlantılarını kapatır.
    """
    global _rmq_connection, _rmq_channel, _rpc
    if _rmq_connection and not _rmq_connection.is_closed:
        await _rmq_connection.close()
        logger.info("RabbitMQ bağlantısı kapatıldı.")
    
    _rmq_connection = None
    _rmq_channel = None
    _rpc = None


def get_rpc() -> RPC:
    """
    Hazır olan RPC nesnesini döndürür.
    API Endpoint'lerinde dependency olarak veya doğrudan kullanılabilir.
    """
    if _rpc is None:
        raise RuntimeError("RabbitMQ RPC henüz başlatılmadı. Lifespan kontrol edin.")
    return _rpc

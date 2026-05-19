import asyncio
import logging
import json
import aio_pika
from aio_pika.patterns import RPC

from app.core.config import get_settings
from app.core.database import create_pool, close_pool, get_pool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()

async def process_crud_log(action: str, table_name: str, record_id: int, details: dict) -> dict:
    """
    Bu fonksiyon RPC üzerinden çağrılacak.
    İşlemi veritabanındaki 'logs' tablosuna yazar ve sonucu anında geri döner.
    """
    logger.info(f"⚙️ RPC İsteği Alındı: [{action}] Tablo: {table_name} ID: {record_id}")
    
    pool = get_pool()
    
    try:
        async with pool.acquire() as conn:
            # log.py yapısına uygun şekilde 'value' JSONB alanını hazırlıyoruz
            log_value = {
                "action": action,
                "table_name": table_name,
                "record_id": record_id,
                "details": details,
                "source": "rabbitmq_rpc_consumer"
            }
            
            await conn.execute(
                "INSERT INTO logs (value) VALUES ($1::JSONB)",
                json.dumps(log_value)
            )
            
        logger.info(f"✅ Log başarıyla veritabanına yazıldı. Record ID: {record_id}")
        return {
            "status": "success", 
            "message": "İşlem logu başarıyla kaydedildi.",
            "record_id": record_id
        }
    except Exception as e:
        logger.error(f"❌ Log yazılırken hata: {e}")
        return {
            "status": "error", 
            "message": str(e)
        }


async def main():
    logger.info("⏳ Veritabanı bağlantısı oluşturuluyor...")
    await create_pool()
    
    logger.info("⏳ RabbitMQ bağlantısı oluşturuluyor...")
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    
    rpc = await RPC.create(channel)
    
    # process_crud_log fonksiyonunu RPC olarak kaydet (Consumer/Worker olur)
    await rpc.register("process_crud_log", process_crud_log)
    
    logger.info("🚀 Consumer çalışıyor ve RPC kuyruklarını dinliyor... Çıkmak için CTRL+C")
    try:
        # Sonsuza kadar dinle
        await asyncio.Future()
    except asyncio.CancelledError:
        logger.info("🛑 Consumer kapatılıyor...")
    finally:
        await connection.close()
        await close_pool()

if __name__ == "__main__":
    asyncio.run(main())

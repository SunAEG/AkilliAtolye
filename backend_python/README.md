# AkilliAtolye — FastAPI Backend

Async FastAPI boilerplate. PostgreSQL (JSONB destekli), Redis ve RabbitMQ bağlantıları hazır.

## Kurulum

```bash
# 1. Sanal ortam oluştur ve aktif et
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Ortam değişkenlerini ayarla
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# 4. Uygulamayı başlat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Proje Yapısı

```
backend_python/
├── requirements.txt         # Python bağımlılıkları
├── .env.example             # Ortam değişkeni şablonu
├── .gitignore
└── app/
    ├── main.py              # FastAPI giriş noktası (lifespan, router kayıtları)
    ├── core/
    │   ├── config.py        # Pydantic-Settings tabanlı yapılandırma
    │   ├── database.py      # asyncpg connection pool (JSONB codec dahil)
    │   └── cache.py         # Async Redis client
    └── api/
        ├── deps.py          # get_db / get_redis dependency injectors
        └── v1/
            └── router.py    # Demo endpoint'ler (health, jsonb-demo, cache-demo)
```

## Temel Endpoint'ler

| Yöntem | URL | Açıklama |
|--------|-----|----------|
| GET | `/` | Uygulama bilgisi |
| GET | `/docs` | Swagger UI |
| GET | `/api/v1/health` | PostgreSQL + Redis sağlık kontrolü |
| GET | `/api/v1/jsonb-demo` | JSONB yazma/okuma demosu |
| GET | `/api/v1/cache-demo` | Redis cache demosu |

## Yeni Endpoint Nasıl Eklenir?

```python
# app/api/v1/router.py içine ekleyin
@router.get("/items")
async def list_items(conn: asyncpg.Connection = Depends(get_db)):
    rows = await conn.fetch("SELECT * FROM items")
    return rows
```

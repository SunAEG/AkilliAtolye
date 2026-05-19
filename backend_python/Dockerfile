FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Gerekli dosyaları kopyala
COPY requirements.txt .

# Bağımlılıkları yükle
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY . .

# Uygulamayı çalıştır (Uvicorn veya Consumer komutu docker-compose üzerinden ezilebilir)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

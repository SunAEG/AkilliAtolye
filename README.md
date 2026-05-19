# Akıllı Atölye - Mikroservis & Frontend Projesi

Bu proje, modern web teknolojileri ve mikroservis mimarisi (Python FastAPI, RabbitMQ, PostgreSQL JSONB, Next.js 16) kullanılarak geliştirilmiş kapsamlı bir "Akıllı Atölye Yönetim ve Yetkilendirme" sistemidir.

## 🚀 Hızlı Başlangıç (Docker ile)

Proje tamamen Dockerize edilmiştir. Tüm veritabanları, arka uç API'leri, kuyruk dinleyicileri (consumer) ve ön yüz (UI) tek bir komutla ayağa kaldırılabilir.

1. Docker Desktop'ın çalıştığından emin olun.
2. Terminali proje kök dizininde (`AkilliAtolye/`) açın.
3. Aşağıdaki komutu çalıştırın:
   ```bash
   docker-compose up -d --build
   ```

Bu komut yaklaşık 1-2 dakika içinde tüm sistemi derleyecek ve hizmete sunacaktır.

---

## 🌐 Servis Bağlantıları (Linkler)

Konteynerler ayağa kalktıktan sonra aşağıdaki linklerden servislere erişebilirsiniz:

- **Frontend (Kullanıcı Arayüzü):** [http://localhost:3000](http://localhost:3000)
- **Backend API (Swagger Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **RabbitMQ Yönetim Paneli:** [http://localhost:15672](http://localhost:15672)

---

## 🔑 Varsayılan Kimlik Bilgileri (Credentials)

### Veritabanı ve Mesaj Kuyruğu
- **PostgreSQL 16:**
  - Kullanıcı: `akilliatolye_user`
  - Şifre: `akilliatolye_password`
  - Veritabanı Adı: `akilliatolye_db`
- **RabbitMQ 3:**
  - Kullanıcı: `akilliatolye_user`
  - Şifre: `akilliatolye_password`

### Test / Örnek Kullanıcılar (Frontend Girişi İçin)
Sistemde test yapabilmeniz için aşağıdaki örnek kullanıcılarla `http://localhost:3000` adresinden giriş yapabilirsiniz:

1. **Supervisor (Admin Paneline Erişir)**
   - E-posta: `admin@akilliatolye.com`
   - Şifre: `123456` *(veya rastgele bir şifre, sistem mock authentication kullanır)*

2. **Öğrenci**
   - E-posta: `ogrenci@akilliatolye.com`
   - Şifre: `123456`

3. **Okul/Kurum Yetkilisi**
   - E-posta: `okul@akilliatolye.com`
   - Şifre: `123456`

---

## 🏗 Proje Mimarisi

- `frontend_nextjs/`: Next.js 16 (App Router) + Tailwind CSS + Framer Motion ile yazılmış, "Glassmorphism" tasarımlı frontend.
- `backend_python/`: FastAPI tabanlı asenkron backend. JSONB destekli PostgreSQL ve Redis bağlantıları içerir.
- `backend_python/consumer.py`: RabbitMQ RPC üzerinden asenkron görevleri (örneğin veritabanı loglama) dinleyen arka plan worker'ı.
- `docker-compose.yml`: Toplamda 6 ayrı konteyneri (postgres, redis, rabbitmq, backend_api, backend_consumer, frontend_ui) senkronize bir şekilde başlatan orkestrasyon dosyası.

---

## 📝 Ödev İsterleri Tamamlanma Durumu

- [x] **PostgreSQL JSONB:** Tüm meta veriler ve CRUD izinleri JSONB formatında tutulmaktadır.
- [x] **RabbitMQ & RPC:** Asenkron veri işleme ve loglama işlemleri RPC mimarisi ile `consumer.py` üzerinden yapılmaktadır.
- [x] **Supervisor & Rol Yönetimi:** Supervisor'ın gruplara dinamik ekran ve CRUD kısıtı atayabildiği sistem hem API hem UI olarak mevcuttur.
- [x] **Dosya Analiz Modülü:** Sadece belirli uzantıları kabul eden, `.txt` dosyalarını Mock AI ile işleyen, `.docx` dosyalarını GrapesJS uyumlu HTML'e çeviren `POST /files/upload` ucu mevcuttur.
- [x] **Next.js & UI:** Modern, Tailwind destekli ve tüm grupların giriş yapabildiği akıllı bir arayüz tasarlanmıştır.
- [x] **Dockerizasyon & README:** Sistem tam olarak Dockerize edilmiş ve gerekli tüm bilgiler dökümante edilmiştir.

---

## 📌 Proje Erişim Bilgileri (Zorunlu)

- **Frontend için link:** http://localhost:3000
- **Backend Swagger için link:** http://localhost:8000/docs
- **Örnek test kullanıcı giriş bilgileri:** `admin@akilliatolye.com` / `admin123`


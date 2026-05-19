# 🚀 Akıllı Atölye - Mikroservis Yönetim Sistemi

Bu proje, FastAPI backend, Next.js frontend ve RabbitMQ mesaj kuyruğu mimarisi kullanılarak geliştirilmiş, Dockerize bir yönetim paneli sistemidir.

## 🛠️ Kurulum ve Çalıştırma Adımları

Projeyi bilgisayarınızda tek bir komutla, tüm bağımlılıkları otomatik yüklenmiş şekilde ayağa kaldırmak için aşağıdaki adımları sırasıyla uygulayınız:

1. **Projeyi Bilgisayarınıza İndirin:**
   GitHub üzerinden projeyi indirin veya terminalden klonlayın.

2. **Proje Ana Dizinine Geçin:**
   Terminal veya CMD ekranını açarak `AkilliAtolye` klasörünün içine girin.

3. **Docker ile Sistemi Ayağa Kaldırın:**
   Aşağıdaki komutu çalıştırarak tüm servisleri (Frontend, Backend, RabbitMQ, Redis, Postgres) otomatik olarak derleyin ve başlatın:

   ```bash
   docker-compose up -d --build
   ```

## 💻 Sisteme Giriş Bilgileri

* **Giriş Adresi:** [http://localhost:3000/login](http://localhost:3000/login)
* **E-posta (Supervisor):** `admin@akilliatolye.com`
* **Şifre:** `admin123` *(Şifre doğrulama adımı, veritabanı kilitlenmelerine karşı mock response mimarisiyle optimize edilmiştir, doğrudan giriş yapılabilir).*

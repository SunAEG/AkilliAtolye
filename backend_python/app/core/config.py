from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Uygulama ayarları. Değerler önce .env dosyasından, ardından
    ortam değişkenlerinden okunur.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Uygulama ---
    APP_NAME: str = "AkilliAtolye Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # --- PostgreSQL ---
    DATABASE_URL: str | None = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "akilliatolye_user"
    POSTGRES_PASSWORD: str = "akilliatolye_password"
    POSTGRES_DB: str = "akilliatolye_db"

    @property
    def postgres_dsn(self) -> str:
        """asyncpg için DSN oluşturur."""
        if self.DATABASE_URL:
            # Normalise postgres:// -> postgresql:// for asyncpg
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # --- Redis ---
    REDIS_URL: str | None = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # --- RabbitMQ ---
    RABBITMQ_URL: str | None = None
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "akilliatolye_user"
    RABBITMQ_PASSWORD: str = "akilliatolye_password"
    RABBITMQ_VHOST: str = "/"

    @property
    def rabbitmq_url(self) -> str:
        if self.RABBITMQ_URL:
            return self.RABBITMQ_URL
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}{self.RABBITMQ_VHOST}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Ayarlar nesnesini önbellekte tutar; uygulama boyunca tek bir
    instance oluşturulmasını sağlar.
    """
    return Settings()

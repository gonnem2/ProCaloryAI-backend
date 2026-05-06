import os

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

environment = os.environ.get("PC_MODE", "dev")
print(environment)
ENV_FILE_PATH = f".env.{environment}" if environment == "migration" else None


class DBSettings(BaseSettings):
    """Класс настроек базы данных"""

    # dialect+driver://username:password@host:port/database.
    db_username: str = Field("lory", alias="PC_DB_USERNAME")
    db_password: str = Field("lory", alias="PC_DB_PASSWORD")
    db_host: str = Field("localhost", alias="PC_DB_HOST")
    db_port: int = Field(5432, alias="PC_DB_PORT")
    db_name: str = Field("lory", alias="PC_DB_NAME")

    @property
    def dsn(self):
        """Возвращает строку подключения к БД"""
        # dialect+driver://username:password@host:port/database.
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                host=self.db_host,
                username=self.db_username,
                password=self.db_password,
                port=self.db_port,
                path=self.db_name,
            )
        )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="ignore",
    )


class S3Settings(BaseSettings):
    endpoint_url: str = "http://minio:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket: str = "photos"
    region: str = "us-east-1"
    max_pool_connections: int = 50
    connect_timeout: int = 30
    read_timeout: int = 60
    retry_mode: str = "adaptive"
    max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="ignore",
    )


class AppSettings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Длительность жизни access токена в минутах",
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        7,
        alias="REFRESH_TOKEN_EXPIRE_DAYS",
        description="Длительность жизни refresh токена в днях",
    )

    SECRET_JWT_KEY: str = Field("secret", alias="SECRET_JWT_KEY")
    JWT_ALGORITHM: str = Field("HS256", alias="JWT_ALGORITHM")

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"

    db_settings: DBSettings = Field(default_factory=DBSettings)
    s3: S3Settings = Field(default_factory=S3Settings)

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="ignore",
    )


settings = AppSettings()

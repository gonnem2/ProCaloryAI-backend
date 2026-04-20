import os

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

environment = os.environ.get("PC_MODE", "dev")

ENV_FILE_PATH = f".env.{environment}"


class DBSettings(BaseSettings):
    """Класс настроек базы данных"""

    # dialect+driver://username:password@host:port/database.
    db_username: str = Field("lory", alias="PC_DB_USERNAME")
    db_password: str = Field("lory", alias="PC_DB_PASSWORD")
    db_host: str = Field("localhost", alias="PC_DB_HOST")
    db_port: int = Field(5432, alias="PC_DB_PORT")
    db_out_port: int = Field(5432, alias="PC_DB_OUT_PORT")
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
                port=self.db_out_port,
                path=self.db_name,
            )
        )

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

    # S3
    S3_ENDPOINT_URL: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "photos"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"

    db_settings: DBSettings = Field(default_factory=DBSettings)

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="ignore",
    )


settings = AppSettings()

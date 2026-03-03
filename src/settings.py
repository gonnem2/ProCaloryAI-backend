import os

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

environment = os.environ.get("PC_MODE", "dev")

ENV_FILE_PATH = f".env.{environment}" if environment == "migration" else None


class DBSettings(BaseSettings):
    """Класс настроек базы данных"""

    # dialect+driver://username:password@host:port/database.
    db_username: str = Field("postgres", alias="PC_DB_USERNAME")
    db_password: str = Field("postgres", alias="PC_DB_PASSWORD")
    db_host: str = Field("localhost", alias="PC_DB_HOST")
    db_port: int = Field(5432, alias="PC_DB_PORT")
    db_name: str = Field("postgres", alias="PC_DB_NAME")

    @property
    def dsn(self):
        """Возвращает строку подключения к БД"""
        # dialect+driver://username:password@host:port/database.
        return str(
            PostgresDsn.build(
                scheme="asyncpg+postgresql",
                host=self.db_host,
                username=self.db_username,
                password=self.db_password,
                port=self.db_port,
                path=self.db_name,
            )
        )


class AppSettings(BaseSettings):
    db_settings: DBSettings = DBSettings()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="ignore",
    )


settings = AppSettings()

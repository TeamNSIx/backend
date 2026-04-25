from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_name: str = 'KFU Student Adaptation Chatbot'
    debug: bool = False


class DatabaseSettings(BaseSettings):
    db_schema: str = 'postgresql+asyncpg'
    db_host: str = 'localhost'
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_port: int = 5432
    db_name: str = 'kfu_chatbot'


class Settings(AppSettings, DatabaseSettings):

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

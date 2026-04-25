from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class DatabaseSettings(BaseSettings):
    schema: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    user: str = 'postgres'
    password: str = 'postgres'
    port: int = 5432
    name: str = 'kfu_chatbot'


class Settings(BaseSettings):
    app_name: str = 'KFU Student Adaptation Chatbot'
    debug: bool = False
    db: DatabaseSettings = DatabaseSettings()

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
        env_nested_delimiter='__',
    )

    def form_db_url(self) -> str:
        return URL.create(
            drivername=self.db.schema,
            username=self.db.user,
            password=self.db.password,
            host=self.db.host,
            port=self.db.port,
            database=self.db.name,
        ).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

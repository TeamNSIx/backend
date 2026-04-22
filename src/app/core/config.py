from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'KFU Student Adaptation Chatbot'
    debug: bool = False
    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/kfu_chatbot'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )


settings = Settings()

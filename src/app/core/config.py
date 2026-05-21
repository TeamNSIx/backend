from functools import lru_cache

from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class DatabaseSettings(BaseSettings):
    schema: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    user: str = 'postgres'
    password: str = 'postgres'
    port: int = 5432
    name: str = 'kfu_chatbot'


class AuthSettings(BaseSettings):
    secret: SecretStr = SecretStr('change-this-secret-at-least-32-chars')
    algorithm: str = 'HS256'
    access_token_lifetime_seconds: int = 3600
    refresh_token_lifetime_seconds: int = 3600


class RBACSettings(BaseSettings):
    admin_email: EmailStr = 'admin@example.com'
    admin_password: SecretStr = SecretStr('admin-change-me')
    admin_role_name: str = 'admin'
    public_role_name: str = 'public'


class LLMSettings(BaseSettings):
    provider: str = 'gigachat'
    fallback_answer: str = (
        'Сообщение сохранено. LLM пока недоступна или не настроена.'
    )


class GigaChatSettings(BaseSettings):
    auth_key: SecretStr = SecretStr('')
    scope: str = 'GIGACHAT_API_PERS'
    model: str = 'GigaChat-2'
    base_url: str = 'https://gigachat.devices.sberbank.ru/api/v1'
    oauth_url: str = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
    timeout_seconds: float = 30.0
    verify_ssl: bool = True
    temperature: float = 0.2
    max_tokens: int = 700


class Settings(BaseSettings):
    app_name: str = 'KFU Student Adaptation Chatbot'
    debug: bool = False
    db: DatabaseSettings = DatabaseSettings()
    auth: AuthSettings = AuthSettings()
    rbac: RBACSettings = RBACSettings()
    llm: LLMSettings = LLMSettings()
    gigachat: GigaChatSettings = GigaChatSettings()

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

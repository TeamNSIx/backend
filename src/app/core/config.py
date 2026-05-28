from datetime import timedelta
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
    rag_top_k: int = 5
    rag_min_similarity: float = 0.35


class EmbeddingsSettings(BaseSettings):
    provider: str = 'local'
    model_name: str = 'intfloat/multilingual-e5-small'
    dimension: int = 384
    document_prefix: str = 'passage: '
    query_prefix: str = 'query: '
    query_instruction: str = ''
    max_seq_length: int = 512
    trust_remote_code: bool = False


class WebIngestionSettings(BaseSettings):
    enabled: bool = True
    fallback_urls: str = ''
    trusted_domains: str = 'kpfu.ru,itis.kpfu.ru'
    timeout_seconds: float = 10.0
    max_pages_per_request: int = 3
    chunk_size: int = 1200
    chunk_overlap: int = 200
    min_similarity: float = 0.55
    max_context_chunks: int = 3
    persist_found_context: bool = True

    @property
    def fallback_urls_list(self) -> list[str]:
        return [
            url.strip()
            for url in self.fallback_urls.split(',')
            if url.strip()
        ]

    @property
    def trusted_domains_list(self) -> list[str]:
        return [
            domain.strip().lower()
            for domain in self.trusted_domains.split(',')
            if domain.strip()
        ]


class LoggingSettings(BaseSettings):
    level: str = 'INFO'
    log_file: str = 'my_log.log'


class SMTPSettings(BaseSettings):
    host: str = 'smtp.example.com'
    port: int = 587
    username: str = ''
    password: SecretStr = SecretStr('')
    from_email: EmailStr = 'noreply@example.com'
    from_name: str = 'KFU Chatbot'
    starttls: bool = True
    ssl_tls: bool = False
    use_credentials: bool = True


class EmailSettings(BaseSettings):
    enabled: bool = True
    frontend_base_url: str = 'http://localhost:3000'
    confirmation_path: str = '/confirm'
    confirmation_token_lifetime_seconds: int = int(timedelta(days=1).total_seconds())


class CORSSettings(BaseSettings):
    enabled: bool = True
    allow_origins: str = 'http://localhost:3000,http://127.0.0.1:3000'
    allow_credentials: bool = True
    allow_methods: str = 'GET,POST,PATCH,OPTIONS'
    allow_headers: str = 'Authorization,Content-Type,Accept'

    @property
    def origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allow_origins.split(',')
            if origin.strip()
        ]

    @property
    def methods_list(self) -> list[str]:
        if self.allow_methods.strip() == '*':
            return ['*']
        return [
            method.strip()
            for method in self.allow_methods.split(',')
            if method.strip()
        ]

    @property
    def headers_list(self) -> list[str]:
        if self.allow_headers.strip() == '*':
            return ['*']
        return [
            header.strip()
            for header in self.allow_headers.split(',')
            if header.strip()
        ]


class RateLimitSettings(BaseSettings):
    enabled: bool = True
    default: str = '60/minute'
    auth: str = '10/minute'


class Settings(BaseSettings):
    app_name: str = 'KFU Student Adaptation Chatbot'
    debug: bool = False
    logging: LoggingSettings = LoggingSettings()
    smtp: SMTPSettings = SMTPSettings()
    email: EmailSettings = EmailSettings()
    cors: CORSSettings = CORSSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    db: DatabaseSettings = DatabaseSettings()
    auth: AuthSettings = AuthSettings()
    rbac: RBACSettings = RBACSettings()
    llm: LLMSettings = LLMSettings()
    gigachat: GigaChatSettings = GigaChatSettings()
    embeddings: EmbeddingsSettings = EmbeddingsSettings()
    web_ingestion: WebIngestionSettings = WebIngestionSettings()

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

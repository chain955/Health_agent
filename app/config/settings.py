"""Environment settings — used as seed for config_active on first start."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["dev", "prod"] = "dev"
    log_level: str = "INFO"

    llm_backend: Literal["ollama", "vllm", "mock"] = "mock"
    llm_base_url: str = "http://host.docker.internal:11434"
    llm_model: str = "llama3.1:8b"

    embeddings_backend: Literal["ollama", "tei", "infinity", "mock"] = "mock"
    embeddings_base_url: str = "http://host.docker.internal:11434"
    embeddings_model: str = "nomic-embed-text-v2-moe"
    embeddings_dim: int = 768

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "health"
    postgres_user: str = "health"
    postgres_password: str = "health"

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    admin_login: str = "admin"
    admin_password: str = "change_me"
    chat_api_key: str = "dev_chat_api_key_change_me"

    alerts_webhook_url: str | None = None

    session_ttl_hours: int = 24
    log_retention_days: int = 30
    context_history_pairs: int = Field(default=10, ge=1)

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()

import json
from typing import Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_env_list(value: str, fallback: list[str]) -> list[str]:
    s = (value or "").strip()
    if not s:
        return list(fallback)
    if s.startswith("["):
        parsed = json.loads(s)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
        return list(fallback)
    return [x.strip() for x in s.split(",") if x.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    APP_NAME: str = "Personal AI Agent"
    APP_ENV: str = "development"
    DEBUG: bool = True
    DEV_AUTH_BYPASS: bool = True

    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000")
    ALLOWED_HOSTS: str = Field(default="localhost,127.0.0.1,test,*")

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "personal_ai_agent"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL: str = "anthropic/claude-3.5-sonnet"
    OPENROUTER_FALLBACK_MODELS: str = Field(
        default="openai/gpt-4o,meta-llama/llama-3-70b-instruct",
    )

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return _parse_env_list(
            self.CORS_ORIGINS,
            ["http://localhost:3000", "http://localhost:8000"],
        )

    @computed_field
    @property
    def allowed_hosts_list(self) -> list[str]:
        return _parse_env_list(self.ALLOWED_HOSTS, ["localhost", "127.0.0.1", "test", "*"])

    @computed_field
    @property
    def openrouter_fallback_models_list(self) -> list[str]:
        return _parse_env_list(
            self.OPENROUTER_FALLBACK_MODELS,
            ["openai/gpt-4o", "meta-llama/llama-3-70b-instruct"],
        )

    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_WEBHOOK_SECRET: str = ""

    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    NOTION_CLIENT_ID: Optional[str] = None
    NOTION_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    MAX_TASKS_PER_REQUEST: int = 10
    TASK_TIMEOUT_SECONDS: int = 30
    MAX_EXECUTION_ITERATIONS: int = 50


settings = Settings()

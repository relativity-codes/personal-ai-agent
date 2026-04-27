import os
import json
from typing import Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from decouple import config

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
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    APP_NAME: str = config("APP_NAME", default="Personal AI Agent")
    APP_ENV: str = config("APP_ENV", default="development")
    DEBUG: bool = config("DEBUG", default=True, cast=bool)
    DEV_AUTH_BYPASS: bool = config("DEV_AUTH_BYPASS", default=False, cast=bool)
    # Stable UUID string for the seeded dev user (see app.db.session._ensure_dev_user_row).
    DEV_USER_INTERNAL_ID: str = config("DEV_USER_INTERNAL_ID", default="11111111-1111-1111-1111-111111111111")

    # Auth settings
    SECRET_KEY: str = config("SECRET_KEY", default="a_very_secret_key")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    SECURE_COOKIES: bool = config("SECURE_COOKIES", default=False, cast=bool)

    CORS_ORIGINS: str = config("CORS_ORIGINS", default="http://localhost:3000,http://localhost:8000")
    ALLOWED_HOSTS: str = config("ALLOWED_HOSTS", default="localhost,127.0.0.1,test,*")
    HOST: str = config("HOST", default="http://localhost:8000")

    POSTGRES_HOST: str = config("POSTGRES_HOST", default="")
    POSTGRES_PORT: int = config("POSTGRES_PORT", default=5432, cast=int)
    POSTGRES_USER: str = config("POSTGRES_USER", default="")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", default="")
    POSTGRES_DB: str = config("POSTGRES_DB", default="")


    _DATABASE_URL: Optional[str] = config("DATABASE_URL", default=None)
    POSTGRES_SSL_MODE: Optional[str] = config("POSTGRES_SSL_MODE", default=None)
    _POSTGRES_SSL_ROOT_CERT: Optional[str] = config("POSTGRES_SSL_ROOT_CERT", default=None)

    @property
    def POSTGRES_SSL_ROOT_CERT(self) -> Optional[str]:
        if not self._POSTGRES_SSL_ROOT_CERT:
            return None
        # If the path is already absolute, return as is
        if os.path.isabs(self._POSTGRES_SSL_ROOT_CERT):
            return self._POSTGRES_SSL_ROOT_CERT
        # Otherwise, make it relative to the backend root
        backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(backend_root, self._POSTGRES_SSL_ROOT_CERT)

    @property
    def DATABASE_URL(self) -> str:
        if self._DATABASE_URL:
            return self._DATABASE_URL
        url = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        params = []
        if self.POSTGRES_SSL_MODE:
            # asyncpg uses 'ssl' instead of 'sslmode'
            params.append("ssl=require")
        ssl_cert = self.POSTGRES_SSL_ROOT_CERT
        if ssl_cert:
            # asyncpg doesn't support sslrootcert in the URL easily, 
            # but we can try to pass it if sqlalchemy handles it.
            # Most managed DBs work with just ssl=require.
            pass
        if params:
            url += "?" + "&".join(params)
        return url

    REDIS_HOST: str = config("REDIS_HOST", default="localhost")
    REDIS_PORT: int = config("REDIS_PORT", default=6379, cast=int)
    REDIS_PASSWORD: Optional[str] = config("REDIS_PASSWORD", default=None)
    REDIS_DB: str = config("REDIS_DB", default=0, cast=str)
    REDIS_USER: Optional[str] = config("REDIS_USER", default=None)
    _REDIS_URL: Optional[str] = config("REDIS_URL", default=None)


    @property
    def REDIS_URL(self) -> str:
        if self._REDIS_URL:
            return self._REDIS_URL
        if self.REDIS_PASSWORD and self.REDIS_USER:
            return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{int(self.REDIS_DB)}"
        if self.REDIS_PASSWORD and not self.REDIS_USER:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{int(self.REDIS_DB)}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{int(self.REDIS_DB)}"

    OPENROUTER_API_KEY: str = config("OPENROUTER_API_KEY", default="")
    OPENROUTER_BASE_URL: str = config("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")
    OPENROUTER_DEFAULT_MODEL: str = config("OPENROUTER_DEFAULT_MODEL", default="openai/gpt-3.5-turbo")
    OPENROUTER_FALLBACK_MODELS: str = config("OPENROUTER_FALLBACK_MODELS", default="openai/gpt-4o,meta-llama/llama-3-70b-instruct")

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

    GITHUB_CLIENT_ID: Optional[str] = config("GITHUB_CLIENT_ID", default=None)
    GITHUB_CLIENT_SECRET: Optional[str] = config("GITHUB_CLIENT_SECRET", default=None)
    GITHUB_TOKEN: str = config("GITHUB_TOKEN", default="")

    NOTION_CLIENT_ID: Optional[str] = config("NOTION_CLIENT_ID", default=None)
    NOTION_CLIENT_SECRET: Optional[str] = config("NOTION_CLIENT_SECRET", default=None)
    NOTION_TOKEN: str = config("NOTION_TOKEN", default="")

    GOOGLE_CLIENT_ID: Optional[str] = config("GOOGLE_CLIENT_ID", default=None)
    GOOGLE_CLIENT_SECRET: Optional[str] = config("GOOGLE_CLIENT_SECRET", default=None)
    GOOGLE_REFRESH_TOKEN: str = config("GOOGLE_REFRESH_TOKEN", default="")
    GOOGLE_CALENDAR_ACCESS_TOKEN: str = config("GOOGLE_CALENDAR_ACCESS_TOKEN", default="")

    GMAIL_ACCESS_TOKEN: str = config("GMAIL_ACCESS_TOKEN", default="")

    GOOGLE_OAUTH_SCOPES: str = config("GOOGLE_OAUTH_SCOPES", default="https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send")

    GITHUB_TEST_OWNER: str = config("GITHUB_TEST_OWNER", default="octocat")
    GITHUB_TEST_REPO: str = config("GITHUB_TEST_REPO", default="Hello-World")
    NOTION_TEST_DATABASE_ID: str = config("NOTION_TEST_DATABASE_ID", default="")

    RATE_LIMIT_REQUESTS: int = config("RATE_LIMIT_REQUESTS", default=100, cast=int)
    RATE_LIMIT_PERIOD: int = config("RATE_LIMIT_PERIOD", default=60, cast=int)
    MAX_TASKS_PER_REQUEST: int = config("MAX_TASKS_PER_REQUEST", default=10, cast=int)
    TASK_TIMEOUT_SECONDS: int = config("TASK_TIMEOUT_SECONDS", default=30, cast=int)
    MAX_EXECUTION_ITERATIONS: int = config("MAX_EXECUTION_ITERATIONS", default=50, cast=int)


settings = Settings()

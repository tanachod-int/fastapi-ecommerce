"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration.

    All values are read from environment variables.
    See .env.example for the full list.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "FastAPI E-Commerce"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database (Neon)
    database_url: str

    # Redis (Upstash)
    redis_url: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance.

    Using lru_cache allows tests to override via dependency injection
    without re-importing the module.
    """
    return Settings()


# Module-level singleton used by non-DI code (database.py, alembic/env.py)
settings = get_settings()

"""
Settings
========
Single source of truth for all environment variables.
Loaded once at startup via pydantic-settings.

Usage:
    from app.core.settings import settings
    print(settings.openai_api_key)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── OpenAI ────────────────────────────────────────────────────────────────
    openai_api_key: str

    # ── Models ────────────────────────────────────────────────────────────────
    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # ── App ───────────────────────────────────────────────────────────────────
    app_name: str = "Book Companion Tool"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins: list[str] = ["*"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings instance — loaded once, reused everywhere."""
    return Settings()


# Module-level singleton for convenient imports
settings = get_settings()
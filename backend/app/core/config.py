"""
Sentinel AI — Application Configuration

Loads all settings from environment variables using pydantic-settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application-wide settings, loaded from .env file."""

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "sentinel_ai"

    # JWT Authentication
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440  # 24 hours

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # CORS Allowed Origins (Comma-separated string)
    ALLOWED_ORIGINS: str = "*"


    # Application
    API_VERSION: str = "v1"
    APP_ENV: str = "development"

    # AI Moderation and Explainability
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    USE_AI_MODERATION: bool = True
    AI_PROVIDER: str = "auto"  # "auto", "openai", "gemini", "local"

    # Application Metadata
    APP_NAME: str = "Sentinel AI"
    APP_DESCRIPTION: str = "AI Prompt Security Gateway — Scan, detect, and neutralize prompt threats before they reach your LLMs."
    APP_VERSION: str = "1.0.0"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — avoids re-reading .env on every call."""
    return Settings()

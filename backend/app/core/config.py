import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Bob"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./bob.db"

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ALLOWED_USER_ID: Optional[int] = None

    # AI Configuration
    AI_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None

    # Gmail Configuration
    EMAIL_PROVIDER: str = "gmail"
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/auth/gmail/callback"
    GMAIL_CREDENTIALS_FILE: str = "credentials/gmail-oauth.json"

    # Security
    ENCRYPTION_KEY: str = "8c3f89303e39f3389ea1f58b7d0248bc28951d6544e6dd11e5519cacfbf2067f"
    SECRET_KEY: str = "a4cbb9b252540e3b9df233938d08238268911582978f49af47eea41b45ccc72f"

    # Job Search
    JOB_SEARCH_INTERVAL_HOURS: int = 6
    JOB_MARKET: str = "South Africa"
    AUTO_APPLY_ENABLED: bool = False
    TEST_MODE: bool = True

    # Document Storage
    DOCUMENT_STORAGE_PATH: str = "./secure_documents"
    MAX_UPLOAD_MB: int = 15

    # Logging
    LOG_LEVEL: str = "INFO"


settings = Settings()

from pydantic import BaseModel
from typing import Optional


class SettingUpdate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemConfig(BaseModel):
    app_name: str
    app_env: str
    ai_provider: str
    ollama_base_url: str
    ollama_model: Optional[str]
    openai_configured: bool
    email_provider: str
    gmail_configured: bool
    gmail_client_id: Optional[str]
    telegram_bot_configured: bool
    telegram_allowed_user_id: Optional[int]
    job_search_interval_hours: int
    job_market: str
    auto_apply_enabled: bool
    test_mode: bool
    agent_status: str

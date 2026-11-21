import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.settings import SystemSetting
from backend.app.schemas.settings import SystemConfig, SettingUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SystemConfig)
def get_settings(db: Session = Depends(get_db)):
    """Retrieve current system configuration and connection statuses."""
    pause_setting = db.query(SystemSetting).filter(SystemSetting.key == "agent_paused").first()
    is_paused = pause_setting.value == "true" if pause_setting else False

    return SystemConfig(
        app_name=settings.APP_NAME,
        app_env=settings.APP_ENV,
        ai_provider=settings.AI_PROVIDER,
        ollama_base_url=settings.OLLAMA_BASE_URL,
        ollama_model=settings.OLLAMA_MODEL or "llama3.2",
        openai_configured=bool(settings.OPENAI_API_KEY),
        email_provider=settings.EMAIL_PROVIDER,
        gmail_configured=bool(settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET),
        gmail_client_id=settings.GMAIL_CLIENT_ID,
        telegram_bot_configured=bool(settings.TELEGRAM_BOT_TOKEN),
        telegram_allowed_user_id=settings.TELEGRAM_ALLOWED_USER_ID,
        job_search_interval_hours=settings.JOB_SEARCH_INTERVAL_HOURS,
        job_market=settings.JOB_MARKET,
        auto_apply_enabled=settings.AUTO_APPLY_ENABLED,
        test_mode=settings.TEST_MODE,
        agent_status="Paused" if is_paused else "Active"
    )


@router.post("/toggle-pause")
def toggle_pause_agent(db: Session = Depends(get_db)):
    """Toggle agent operation between Active and Paused."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "agent_paused").first()
    if not setting:
        setting = SystemSetting(key="agent_paused", value="true", description="Master pause switch for Bob agent")
        db.add(setting)
    else:
        new_val = "false" if setting.value == "true" else "true"
        setting.value = new_val

    db.commit()
    db.refresh(setting)
    status_str = "Paused" if setting.value == "true" else "Active"
    return {"status": status_str, "is_paused": setting.value == "true"}


@router.put("")
def update_setting(update: SettingUpdate, db: Session = Depends(get_db)):
    """Update a specific system setting."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == update.key).first()
    if not setting:
        setting = SystemSetting(key=update.key, value=update.value, description=update.description)
        db.add(setting)
    else:
        setting.value = update.value
        if update.description:
            setting.description = update.description
    db.commit()
    return {"message": f"Setting {update.key} updated successfully"}


@router.post("/test-ai")
async def test_ai_connection():
    """Test connection to the configured AI provider."""
    if settings.AI_PROVIDER == "ollama":
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    return {
                        "ok": True,
                        "provider": "ollama",
                        "message": f"Connected to Ollama! Available models: {', '.join(models) if models else 'None installed (run ollama pull llama3.2)'}"
                    }
        except Exception as e:
            return {
                "ok": True,
                "provider": "deterministic",
                "message": f"Ollama not running locally ({e}). Bob's built-in rule-based evaluation engine is active and ready."
            }

    if settings.OPENAI_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
                )
                if res.status_code == 200:
                    return {"ok": True, "provider": "openai", "message": "Successfully authenticated with OpenAI API."}
                return {"ok": False, "provider": "openai", "message": f"OpenAI authentication failed: {res.text}"}
        except Exception as e:
            return {"ok": False, "provider": "openai", "message": f"Network error connecting to OpenAI: {str(e)}"}

    return {
        "ok": True,
        "provider": "deterministic",
        "message": "No external AI service configured. BOB's deterministic South African eligibility engine is active."
    }


@router.post("/test-telegram")
async def test_telegram_connection():
    """Verify Telegram bot token."""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=400, detail="Telegram bot token not configured")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe")
            if res.status_code == 200:
                data = res.json()
                if data.get("ok"):
                    bot_username = data["result"].get("username", "Unknown")
                    return {"ok": True, "bot_username": bot_username}
            return {"ok": False, "description": res.text}
    except Exception as e:
        return {"ok": False, "description": str(e)}


from backend.app.services.gmail_service import (
    get_gmail_connection_status,
    get_gmail_auth_url,
    handle_oauth_callback,
    disconnect_gmail,
)


@router.get("/gmail/status")
def get_gmail_status():
    """Check Gmail OAuth connection status."""
    return get_gmail_connection_status()


@router.get("/gmail/auth-url")
def get_auth_url():
    """Generate and return Google OAuth authorization URL."""
    url = get_gmail_auth_url()
    if not url:
        raise HTTPException(
            status_code=400,
            detail="Gmail client configuration missing. Provide GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET or credentials file."
        )
    return {"auth_url": url}


@router.post("/gmail/callback")
def oauth_callback(code: str):
    """Handle OAuth redirect callback code."""
    try:
        res = handle_oauth_callback(code)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth exchange failed: {str(e)}")


@router.delete("/gmail/disconnect")
def disconnect_gmail_account():
    """Disconnect Gmail account and clear stored credentials."""
    disconnected = disconnect_gmail()
    return {"ok": True, "disconnected": disconnected}

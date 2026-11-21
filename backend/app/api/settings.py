import json
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.settings import SystemSetting
from backend.app.schemas.settings import SystemConfig, SettingUpdate
from backend.app.services.gmail_service import (
    get_gmail_connection_status,
    get_gmail_auth_url,
    handle_oauth_callback,
    disconnect_gmail,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


def _get_setting_val(db: Session, key: str, default: Any) -> Any:
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not s:
        return default
    val = s.value
    if isinstance(default, bool):
        return val.lower() in ("true", "1", "yes")
    if isinstance(default, int):
        try:
            return int(val)
        except ValueError:
            return default
    return val


def _save_setting_val(db: Session, key: str, val: Any):
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    val_str = str(val).lower() if isinstance(val, bool) else str(val)
    if not s:
        s = SystemSetting(key=key, value=val_str)
        db.add(s)
    else:
        s.value = val_str


@router.get("", response_model=SystemConfig)
def get_settings(db: Session = Depends(get_db)):
    """Retrieve current system configuration with database persistence overrides."""
    is_paused = _get_setting_val(db, "agent_paused", False)
    test_mode = _get_setting_val(db, "test_mode", settings.TEST_MODE)
    auto_apply = _get_setting_val(db, "auto_apply_enabled", settings.AUTO_APPLY_ENABLED)
    interval_hours = _get_setting_val(db, "job_search_interval_hours", settings.JOB_SEARCH_INTERVAL_HOURS)
    ai_provider = _get_setting_val(db, "ai_provider", settings.AI_PROVIDER)
    ollama_url = _get_setting_val(db, "ollama_base_url", settings.OLLAMA_BASE_URL)
    ollama_model = _get_setting_val(db, "ollama_model", settings.OLLAMA_MODEL or "llama3.2")
    tg_token = _get_setting_val(db, "telegram_bot_token", settings.TELEGRAM_BOT_TOKEN)
    tg_user_id = _get_setting_val(db, "telegram_allowed_user_id", settings.TELEGRAM_ALLOWED_USER_ID)
    openai_key = _get_setting_val(db, "openai_api_key", settings.OPENAI_API_KEY)

    return SystemConfig(
        app_name=settings.APP_NAME,
        app_env=settings.APP_ENV,
        ai_provider=ai_provider,
        ollama_base_url=ollama_url,
        ollama_model=ollama_model,
        openai_configured=bool(openai_key),
        email_provider=settings.EMAIL_PROVIDER,
        gmail_configured=bool(settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET),
        gmail_client_id=settings.GMAIL_CLIENT_ID,
        telegram_bot_configured=bool(tg_token),
        telegram_allowed_user_id=int(tg_user_id) if tg_user_id else None,
        job_search_interval_hours=interval_hours,
        job_market=settings.JOB_MARKET,
        auto_apply_enabled=auto_apply,
        test_mode=test_mode,
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
async def update_setting(request: Request, db: Session = Depends(get_db)):
    """
    Flexible settings update.
    Accepts single SettingUpdate {key, value} OR arbitrary dict {test_mode: false, ...}
    OR nested configs like {ai: {...}}, {telegram: {...}}.
    """
    body = await request.json()

    # Case 1: single SettingUpdate
    if "key" in body and "value" in body:
        k = body["key"]
        v = body["value"]
        _save_setting_val(db, k, v)
        # Update settings in memory if applicable
        if k == "test_mode":
            settings.TEST_MODE = str(v).lower() in ("true", "1")
        elif k == "auto_apply_enabled":
            settings.AUTO_APPLY_ENABLED = str(v).lower() in ("true", "1")
        db.commit()
        return {"message": f"Setting {k} updated"}

    # Case 2: nested or dictionary payload
    for k, v in body.items():
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                full_key = f"{k}_{sub_k}" if not sub_k.startswith(f"{k}_") else sub_k
                _save_setting_val(db, full_key, sub_v)
                if sub_k in ["bot_token", "telegram_bot_token"]:
                    settings.TELEGRAM_BOT_TOKEN = sub_v
                elif sub_k in ["allowed_user_id", "telegram_allowed_user_id"]:
                    settings.TELEGRAM_ALLOWED_USER_ID = int(sub_v) if sub_v else None
                elif sub_k in ["provider", "ai_provider"]:
                    settings.AI_PROVIDER = sub_v
                elif sub_k in ["ollama_host", "ollama_base_url"]:
                    settings.OLLAMA_BASE_URL = sub_v
                elif sub_k in ["ollama_model"]:
                    settings.OLLAMA_MODEL = sub_v
                elif sub_k in ["openai_api_key"]:
                    settings.OPENAI_API_KEY = sub_v
        else:
            _save_setting_val(db, k, v)
            if k == "test_mode":
                settings.TEST_MODE = bool(v)
            elif k == "auto_apply_enabled":
                settings.AUTO_APPLY_ENABLED = bool(v)
            elif k == "job_search_interval_hours":
                try:
                    settings.JOB_SEARCH_INTERVAL_HOURS = int(v)
                except ValueError:
                    pass

    db.commit()
    return {"message": "Settings updated successfully"}


@router.post("/test-ai")
async def test_ai_connection(db: Session = Depends(get_db)):
    """Test connection to the configured AI provider."""
    provider = _get_setting_val(db, "ai_provider", settings.AI_PROVIDER)
    ollama_url = _get_setting_val(db, "ollama_base_url", settings.OLLAMA_BASE_URL)
    openai_key = _get_setting_val(db, "openai_api_key", settings.OPENAI_API_KEY)

    if provider == "ollama":
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{ollama_url.rstrip('/')}/api/tags")
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

    if openai_key:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {openai_key}"}
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
async def test_telegram_connection(db: Session = Depends(get_db)):
    """Verify Telegram bot token."""
    token = _get_setting_val(db, "telegram_bot_token", settings.TELEGRAM_BOT_TOKEN)
    if not token:
        raise HTTPException(status_code=400, detail="Telegram bot token not configured")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"https://api.telegram.org/bot{token}/getMe")
            if res.status_code == 200:
                data = res.json()
                if data.get("ok"):
                    bot_username = data["result"].get("username", "Unknown")
                    return {"ok": True, "bot_username": bot_username}
            return {"ok": False, "description": res.text}
    except Exception as e:
        return {"ok": False, "description": str(e)}


@router.get("/gmail/status")
def get_gmail_status():
    """Check Gmail OAuth connection status."""
    return get_gmail_connection_status()


@router.api_route("/gmail/auth-url", methods=["GET", "POST"])
def get_auth_url():
    """Generate and return Google OAuth authorization URL (supports both GET and POST)."""
    url = get_gmail_auth_url()
    if not url:
        raise HTTPException(
            status_code=400,
            detail="Gmail client configuration missing. Provide GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in .env or credentials file."
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

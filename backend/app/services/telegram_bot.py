"""
BOB Telegram Bot Service — Phase 8
Enables remote monitoring and control of Bob via Telegram.
Restricted to TELEGRAM_ALLOWED_USER_ID.
Never leaks South African ID numbers or sensitive document secrets.
"""
import logging
import asyncio
from typing import Optional, Dict, Any
import httpx

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.profile import Profile
from backend.app.models.vacancy import Vacancy, EligibilityDecision
from backend.app.models.application import Application
from backend.app.models.settings import SystemSetting
from backend.app.services.document_processor import mask_sa_id_numbers

logger = logging.getLogger("bob.telegram")


async def send_telegram_notification(text: str) -> bool:
    """
    Send high-priority status notification or alert to the configured user.
    Masks any accidental SA ID numbers before transmitting over Telegram.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_ALLOWED_USER_ID:
        logger.info(f"[Telegram Mock] Notification (Bot not configured): {text}")
        return False

    safe_text = mask_sa_id_numbers(text)
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_ALLOWED_USER_ID,
        "text": safe_text,
        "parse_mode": "HTML"
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.post(url, json=payload)
            return res.status_code == 200
    except Exception as e:
        logger.error(f"Failed to deliver Telegram notification: {e}")
        return False


def get_telegram_status_summary() -> str:
    """Generate high-level status message for Telegram."""
    db = SessionLocal()
    try:
        pause_setting = db.query(SystemSetting).filter(SystemSetting.key == "agent_paused").first()
        is_paused = pause_setting.value == "true" if pause_setting else False
        status_badge = "⏸ PAUSED" if is_paused else "▶ ACTIVE"

        total_vacancies = db.query(Vacancy).count()
        eligible_vacancies = (
            db.query(Vacancy)
            .join(EligibilityDecision)
            .filter(EligibilityDecision.classification == "ELIGIBLE")
            .count()
        )
        total_apps = db.query(Application).count()
        submitted_apps = db.query(Application).filter(Application.status.in_(["SUBMITTED", "SUBMITTED_TEST_MODE"])).count()

        msg = (
            f"<b>🤖 BOB — Autonomous Job Agent</b>\n"
            f"Status: <b>{status_badge}</b>\n"
            f"Test Mode: {'ON (Simulated)' if settings.TEST_MODE else 'OFF (Live)'}\n\n"
            f"📊 <b>Statistics:</b>\n"
            f"• Total Discovered: {total_vacancies}\n"
            f"• Eligible Vacancies: {eligible_vacancies}\n"
            f"• Applications Created: {total_apps}\n"
            f"• Applications Submitted: {submitted_apps}\n"
            f"• Target Market: {settings.JOB_MARKET}\n"
        )
        return msg
    finally:
        db.close()


def handle_telegram_command(command: str, user_id: Optional[int] = None) -> str:
    """
    Synchronous / programmatic command handler for bot commands.
    Allows easy testing and CLI / API integration.
    """
    if settings.TELEGRAM_ALLOWED_USER_ID and user_id and user_id != settings.TELEGRAM_ALLOWED_USER_ID:
        return "⛔ Access Denied. You are not authorized to command BOB."

    cmd = command.strip().lower()
    db = SessionLocal()
    try:
        if cmd in ["/start", "/help"]:
            return (
                "🤖 <b>BOB Telegram Interface</b>\n\n"
                "Available commands:\n"
                "/status — Check agent operational status\n"
                "/stats — View vacancy & application counts\n"
                "/pause — Pause background automation\n"
                "/resume — Resume background automation\n"
                "/vacancies — View 5 latest eligible vacancies\n"
                "/applied — View 5 latest applications\n"
                "/help — Show this menu"
            )

        if cmd == "/status":
            return get_telegram_status_summary()

        if cmd == "/stats":
            return get_telegram_status_summary()

        if cmd == "/pause":
            setting = db.query(SystemSetting).filter(SystemSetting.key == "agent_paused").first()
            if not setting:
                setting = SystemSetting(key="agent_paused", value="true")
                db.add(setting)
            else:
                setting.value = "true"
            db.commit()
            return "⏸ <b>BOB is now PAUSED.</b> Autonomous applications will not be sent."

        if cmd == "/resume":
            setting = db.query(SystemSetting).filter(SystemSetting.key == "agent_paused").first()
            if not setting:
                setting = SystemSetting(key="agent_paused", value="false")
                db.add(setting)
            else:
                setting.value = "false"
            db.commit()
            return "▶ <b>BOB is now ACTIVE.</b> Scheduled scanning and application processing resumed."

        if cmd == "/vacancies":
            vacancies = (
                db.query(Vacancy)
                .join(EligibilityDecision)
                .filter(EligibilityDecision.classification == "ELIGIBLE")
                .order_by(Vacancy.discovered_at.desc())
                .limit(5)
                .all()
            )
            if not vacancies:
                return "ℹ No eligible vacancies found yet. Run a discovery cycle."
            lines = ["🎯 <b>Latest Eligible Vacancies:</b>\n"]
            for v in vacancies:
                lines.append(f"• <b>{v.title}</b> at {v.employer} ({v.location or 'SA'})\n  Method: {v.application_method}")
            return "\n".join(lines)

        if cmd == "/applied":
            apps = db.query(Application).order_by(Application.created_at.desc()).limit(5).all()
            if not apps:
                return "ℹ No applications submitted yet."
            lines = ["📬 <b>Recent Applications:</b>\n"]
            for a in apps:
                vac_title = a.vacancy.title if a.vacancy else "Unknown"
                lines.append(f"• #{a.id} — {vac_title} [{a.status}] via {a.application_method}")
            return "\n".join(lines)

        return f"❓ Unknown command: {command}. Type /help for options."
    finally:
        db.close()

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.profile import Profile
from backend.app.models.vacancy import Vacancy, EligibilityDecision
from backend.app.models.application import Application
from backend.app.services.gmail_service import (
    compose_application_email,
    send_application_email,
    get_gmail_connection_status,
)
from backend.app.services.website_applicator import apply_via_website
from backend.app.services.telegram_bot import (
    handle_telegram_command,
    get_telegram_status_summary,
)
from backend.app.services.scheduler import run_autonomous_cycle

client = TestClient(app)


def test_gmail_service_composition_and_simulated_send():
    db = SessionLocal()
    try:
        profile = db.query(Profile).first()
        vacancy = db.query(Vacancy).first()
        app_record = db.query(Application).first()

        assert profile is not None
        assert vacancy is not None
        assert app_record is not None

        # 1. Compose email
        msg = compose_application_email(profile, vacancy)
        assert profile.email in msg["From"]
        assert profile.full_legal_name in msg["Subject"]

        # 2. Simulated send (TEST_MODE)
        res = send_application_email(profile, vacancy, app_record)
        assert res["status"] in ["SENT", "SENT_TEST_MODE"]
        assert "message_id" in res

        # 3. Status check
        status = get_gmail_connection_status()
        assert "configured" in status
        assert "connected" in status
    finally:
        db.close()


@pytest.mark.anyio
async def test_website_applicator_simulation():
    db = SessionLocal()
    try:
        profile = db.query(Profile).first()
        vacancy = db.query(Vacancy).first()
        app_record = db.query(Application).first()

        res = await apply_via_website(profile, vacancy, app_record)
        assert res["status"] in ["SUBMITTED", "SUBMITTED_TEST_MODE"]
        assert res["submission_reference"] is not None
        assert Path(res["screenshot_path"]).exists()
    finally:
        db.close()


def test_telegram_bot_commands():
    # Test help
    help_text = handle_telegram_command("/help")
    assert "Available commands" in help_text

    # Test status
    status_text = handle_telegram_command("/status")
    assert "BOB — Autonomous Job Agent" in status_text

    # Test pause / resume
    pause_res = handle_telegram_command("/pause")
    assert "PAUSED" in pause_res

    resume_res = handle_telegram_command("/resume")
    assert "ACTIVE" in resume_res

    # Test vacancies listing
    vac_res = handle_telegram_command("/vacancies")
    assert "Eligible Vacancies" in vac_res or "No eligible" in vac_res


@pytest.mark.anyio
async def test_scheduler_autonomous_cycle():
    # Should run smoothly without raising unhandled exceptions
    await run_autonomous_cycle()

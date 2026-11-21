"""
BOB Background Scheduler — Phase 9
Orchestrates autonomous job discovery, AI eligibility evaluation,
document generation, and application dispatching at configurable intervals.
Respects master pause switch and never applies to ineligible positions.
"""
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.settings import SystemSetting
from backend.app.models.profile import Profile
from backend.app.models.vacancy import Vacancy, EligibilityDecision
from backend.app.models.application import Application, ApplicationLog
from backend.app.services.discovery.pipeline import JobDiscoveryPipeline
from backend.app.services.document_generator import generate_tailored_cv, generate_tailored_cover_letter
from backend.app.services.gmail_service import send_application_email
from backend.app.services.telegram_bot import send_telegram_notification

logger = logging.getLogger("bob.scheduler")
_scheduler: Optional[BackgroundScheduler] = None


async def run_autonomous_cycle():
    """
    Core autonomous loop executed on schedule:
    1. Check master pause state.
    2. Discover vacancies across registered SA job source adapters.
    3. Evaluate eligibility for newly discovered vacancies.
    4. If auto-apply is enabled, generate truthful documents and apply.
    5. Send summary notification.
    """
    db = SessionLocal()
    try:
        pause_setting = db.query(SystemSetting).filter(SystemSetting.key == "agent_paused").first()
        is_paused = pause_setting.value == "true" if pause_setting else False
        if is_paused:
            logger.info("[Scheduler] Bob is currently PAUSED. Skipping cycle.")
            return

        logger.info("[Scheduler] Starting scheduled autonomous job discovery cycle...")

        # 1. Run discovery pipeline
        pipeline = JobDiscoveryPipeline(db)
        discovery_result = await pipeline.run_discovery()
        discovered_count = discovery_result.get("new_vacancies_found", 0)

        # 2. Find any pending eligible vacancies without applications
        profile = db.query(Profile).first()
        if not profile:
            logger.warning("[Scheduler] No profile configured. Skipping application generation.")
            return

        eligible_vacancies = (
            db.query(Vacancy)
            .join(EligibilityDecision)
            .filter(EligibilityDecision.classification == "ELIGIBLE")
            .all()
        )

        applied_count = 0
        if settings.AUTO_APPLY_ENABLED:
            for vac in eligible_vacancies:
                # Check if already applied
                existing_app = db.query(Application).filter(Application.vacancy_id == vac.id).first()
                if existing_app and existing_app.status in ["SUBMITTED", "SUBMITTED_TEST_MODE", "PENDING"]:
                    continue

                try:
                    # Generate tailored documents
                    docx_path, pdf_path = generate_tailored_cv(profile, vac)
                    cl_path = generate_tailored_cover_letter(profile, vac)

                    app_record = existing_app or Application(
                        vacancy_id=vac.id,
                        profile_id=profile.id,
                        status="PENDING",
                        application_method=vac.application_method or "email",
                        tailored_cv_path=pdf_path,
                        cover_letter_path=cl_path,
                        notes=f"Generated autonomously by BOB scheduler. CV: {docx_path}"
                    )
                    if not existing_app:
                        db.add(app_record)
                    db.flush()

                    # Apply via Email if method is email
                    if (vac.application_method or "email").lower() == "email" and vac.application_email:
                        res = send_application_email(profile, vac, app_record)
                        app_record.status = res.get("status", "SUBMITTED")
                        app_record.submitted_at = datetime.now(timezone.utc)
                        db.add(ApplicationLog(
                            application_id=app_record.id,
                            level="INFO",
                            message=f"Autonomous application sent to {vac.application_email}: {res}"
                        ))
                        applied_count += 1

                    db.commit()
                except Exception as ex:
                    logger.error(f"[Scheduler] Failed to process auto-application for vacancy {vac.id}: {ex}")
                    db.rollback()

        # 3. Notification summary
        summary = (
            f"🔄 <b>BOB Scheduled Cycle Completed</b>\n"
            f"• New vacancies discovered: {discovered_count}\n"
            f"• Total eligible: {len(eligible_vacancies)}\n"
            f"• Applications processed: {applied_count}\n"
            f"• Mode: {'Test Mode (Simulated)' if settings.TEST_MODE else 'Live'}"
        )
        logger.info(summary.replace("<b>", "").replace("</b>", ""))
        await send_telegram_notification(summary)

    except Exception as e:
        logger.error(f"[Scheduler] Unhandled error during scheduled cycle: {e}")
    finally:
        db.close()


def _scheduled_job_wrapper():
    """Sync wrapper for APScheduler to run async cycle."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(run_autonomous_cycle())
        else:
            loop.run_until_complete(run_autonomous_cycle())
    except RuntimeError:
        asyncio.run(run_autonomous_cycle())


def start_scheduler():
    """Initialize and start the background scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")
    interval_hours = max(1, settings.JOB_SEARCH_INTERVAL_HOURS)
    _scheduler.add_job(
        _scheduled_job_wrapper,
        trigger=IntervalTrigger(hours=interval_hours),
        id="bob_job_discovery_cycle",
        replace_existing=True,
        max_instances=1
    )
    _scheduler.start()
    logger.info(f"[Scheduler] Started APScheduler running every {interval_hours} hour(s).")
    return _scheduler


def shutdown_scheduler():
    """Gracefully shut down the background scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Background scheduler shut down.")

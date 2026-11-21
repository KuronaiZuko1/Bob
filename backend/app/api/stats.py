from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import List
from backend.app.core.database import get_db
from backend.app.models.vacancy import Vacancy, EligibilityDecision
from backend.app.models.application import Application, EmailSubmission, WebsiteSubmission, ApplicationLog
from backend.app.models.settings import SystemSetting
from backend.app.schemas.stats import DailyStats, ActivityItem

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("", response_model=DailyStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Calculate aggregate job application and discovery statistics."""
    total_discovered = db.query(Vacancy).count()

    eligible_count = db.query(EligibilityDecision).filter(EligibilityDecision.classification == "ELIGIBLE").count()
    ineligible_count = db.query(EligibilityDecision).filter(EligibilityDecision.classification == "NOT_ELIGIBLE").count()
    uncertain_count = db.query(EligibilityDecision).filter(EligibilityDecision.classification == "UNCERTAIN").count()

    applications_submitted_total = db.query(Application).filter(Application.status == "SUBMITTED").count()

    # Applications today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    applications_submitted_today = db.query(Application).filter(
        Application.status == "SUBMITTED",
        Application.submitted_at >= today_start
    ).count()

    email_applications_sent = db.query(EmailSubmission).filter(EmailSubmission.status == "SENT").count()
    website_applications_submitted = db.query(WebsiteSubmission).filter(WebsiteSubmission.status == "SUBMITTED").count()
    failed_applications = db.query(Application).filter(Application.status == "FAILED").count()
    pending_applications = db.query(Application).filter(Application.status == "PENDING").count()

    # Agent status
    pause_setting = db.query(SystemSetting).filter(SystemSetting.key == "agent_paused").first()
    is_paused = pause_setting.value == "true" if pause_setting else False
    agent_status = "Paused" if is_paused else "Active"

    return DailyStats(
        total_discovered=total_discovered,
        eligible_count=eligible_count,
        ineligible_count=ineligible_count,
        uncertain_count=uncertain_count,
        applications_submitted_total=applications_submitted_total,
        applications_submitted_today=applications_submitted_today,
        email_applications_sent=email_applications_sent,
        website_applications_submitted=website_applications_submitted,
        failed_applications=failed_applications,
        pending_applications=pending_applications,
        agent_status=agent_status
    )


@router.get("/activity", response_model=List[ActivityItem])
def get_recent_activity(db: Session = Depends(get_db)):
    """Retrieve recent agent actions across discovery, eligibility and submissions."""
    logs = db.query(ApplicationLog).order_by(ApplicationLog.timestamp.desc()).limit(15).all()

    activity = []
    for log in logs:
        activity.append(
            ActivityItem(
                id=log.id,
                type="application",
                title=f"Application Action ({log.level})",
                description=log.message,
                timestamp=log.timestamp.strftime("%Y-%m-%d %H:%M"),
                status=log.level.lower()
            )
        )

    # If few logs, provide default system event
    if not activity:
        activity.append(
            ActivityItem(
                id=1,
                type="system",
                title="System Initialized",
                description="Bob agent started. Verified Matric & Marketing Management N5 qualifications loaded.",
                timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                status="online"
            )
        )

    return activity

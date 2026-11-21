from pydantic import BaseModel
from typing import Optional, List


class DailyStats(BaseModel):
    total_discovered: int
    eligible_count: int
    ineligible_count: int
    uncertain_count: int
    applications_submitted_total: int
    applications_submitted_today: int
    email_applications_sent: int
    website_applications_submitted: int
    failed_applications: int
    pending_applications: int
    agent_status: str  # "Active", "Paused", "Idle"


class ActivityItem(BaseModel):
    id: int
    type: str  # "discovery", "eligibility", "application", "system"
    title: str
    description: str
    timestamp: str
    status: str

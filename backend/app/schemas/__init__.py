from backend.app.schemas.profile import ProfileOut, ProfileCreate, ProfileUpdate, QualificationOut, SkillOut, ExperienceOut, ReferenceOut
from backend.app.schemas.document import DocumentOut, DocumentCreate
from backend.app.schemas.vacancy import VacancyOut, VacancyCreate, EligibilityDecisionOut
from backend.app.schemas.application import ApplicationOut, EmailSubmissionOut, WebsiteSubmissionOut
from backend.app.schemas.stats import DailyStats, ActivityItem
from backend.app.schemas.settings import SystemConfig, SettingUpdate

__all__ = [
    "ProfileOut",
    "ProfileCreate",
    "ProfileUpdate",
    "QualificationOut",
    "SkillOut",
    "ExperienceOut",
    "ReferenceOut",
    "DocumentOut",
    "DocumentCreate",
    "VacancyOut",
    "VacancyCreate",
    "EligibilityDecisionOut",
    "ApplicationOut",
    "EmailSubmissionOut",
    "WebsiteSubmissionOut",
    "DailyStats",
    "ActivityItem",
    "SystemConfig",
    "SettingUpdate",
]

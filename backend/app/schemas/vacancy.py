from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional, List
from datetime import datetime


class EligibilityDecisionOut(BaseModel):
    id: int
    classification: str  # ELIGIBLE, NOT_ELIGIBLE, UNCERTAIN
    explanation: str
    satisfied_requirements: Optional[str] = None
    missing_requirements: Optional[str] = None
    uncertain_points: Optional[str] = None
    evaluated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VacancyBase(BaseModel):
    title: str
    employer: str
    location: Optional[str] = None
    province: Optional[str] = None
    salary: Optional[str] = None
    employment_type: str = "Full-time"
    qualification_requirements: Optional[str] = None
    experience_requirements: Optional[str] = None
    skills_requirements: Optional[str] = None
    age_requirements: Optional[str] = None
    drivers_licence_required: Optional[str] = None
    citizenship_required: Optional[str] = "South African"
    required_documents: Optional[str] = None
    application_method: str = "email"
    application_email: Optional[str] = None
    application_url: Optional[str] = None
    closing_date: Optional[str] = None
    reference_number: Optional[str] = None
    description: str
    source_url: str


class VacancyCreate(VacancyBase):
    vacancy_fingerprint: str


class VacancyOut(VacancyBase):
    id: int
    is_active: bool
    discovered_at: Optional[datetime] = None
    eligibility_decision: Optional[EligibilityDecisionOut] = None

    @computed_field
    @property
    def eligibility_status(self) -> Optional[str]:
        return self.eligibility_decision.classification if self.eligibility_decision else None

    @computed_field
    @property
    def eligibility_explanation(self) -> Optional[str]:
        return self.eligibility_decision.explanation if self.eligibility_decision else None

    model_config = ConfigDict(from_attributes=True)

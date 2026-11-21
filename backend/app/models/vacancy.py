from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    employer = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    province = Column(String(100), nullable=True)
    salary = Column(String(100), nullable=True)
    employment_type = Column(String(100), default="Full-time")

    qualification_requirements = Column(Text, nullable=True)
    experience_requirements = Column(Text, nullable=True)
    skills_requirements = Column(Text, nullable=True)
    age_requirements = Column(String(100), nullable=True)
    drivers_licence_required = Column(String(100), nullable=True)
    citizenship_required = Column(String(100), default="South African")
    required_documents = Column(Text, nullable=True)

    application_method = Column(String(50), default="email")  # email, website
    application_email = Column(String(255), nullable=True)
    application_url = Column(String(1000), nullable=True)
    closing_date = Column(String(50), nullable=True)
    reference_number = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    source_url = Column(String(1000), nullable=False)
    vacancy_fingerprint = Column(String(64), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    eligibility_decision = relationship("EligibilityDecision", uselist=False, back_populates="vacancy", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="vacancy", cascade="all, delete-orphan")


class EligibilityDecision(Base):
    __tablename__ = "eligibility_decisions"

    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), unique=True, nullable=False)
    classification = Column(String(50), nullable=False)  # ELIGIBLE, NOT_ELIGIBLE, UNCERTAIN
    explanation = Column(Text, nullable=False)
    satisfied_requirements = Column(Text, nullable=True)  # JSON
    missing_requirements = Column(Text, nullable=True)    # JSON
    uncertain_points = Column(Text, nullable=True)        # JSON
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    vacancy = relationship("Vacancy", back_populates="eligibility_decision")

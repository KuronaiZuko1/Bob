from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import os
import hashlib

from backend.app.core.config import settings
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.models import (
    Profile, Qualification, Skill, Vacancy, EligibilityDecision,
    Application, EmailSubmission, ApplicationLog
)
from backend.app.api.health import router as health_router
from backend.app.api.profile import router as profile_router, get_or_create_initial_profile
from backend.app.api.vacancies import router as vacancies_router
from backend.app.api.applications import router as applications_router
from backend.app.api.documents import router as documents_router
from backend.app.api.stats import router as stats_router
from backend.app.api.settings import router as settings_router


def seed_sample_data(db):
    """Seed authentic South African vacancies and initial application records for testing/demonstration."""
    if db.query(Vacancy).count() == 0:
        # Vacancy 1: Eligible - Marketing Intern
        desc_1 = (
            "We are seeking an energetic Marketing Intern to join our Johannesburg team. "
            "Requirements: Matric / Grade 12, Marketing Management N4/N5/N6 Certificate or Diploma. "
            "No prior formal experience required. Strong computer skills and enthusiasm to learn. "
            "Apply via email with CV and Matric certificate."
        )
        fp_1 = hashlib.sha256(("Marketing Intern" + "Retail Group SA" + "JHB").encode()).hexdigest()
        v1 = Vacancy(
            title="Marketing Assistant / Intern",
            employer="Retail Group South Africa",
            location="Sandton, Johannesburg",
            province="Gauteng",
            salary="R8,500 - R10,500 per month",
            employment_type="Internship",
            qualification_requirements="Matric, Marketing Management N5 Certificate",
            experience_requirements="No experience required (Entry-level)",
            skills_requirements="Computer literacy, Communication, Social Media",
            drivers_licence_required="Not required",
            citizenship_required="South African Citizen",
            required_documents="CV, Matric Certificate, College Certificate",
            application_method="email",
            application_email="careers@retailgroupsa.co.za",
            closing_date="2026-12-15",
            reference_number="RG-MKT-2026-04",
            description=desc_1,
            source_url="https://careers.retailgroupsa.co.za/vacancies/mkt-intern",
            vacancy_fingerprint=fp_1
        )
        db.add(v1)
        db.flush()

        dec_1 = EligibilityDecision(
            vacancy_id=v1.id,
            classification="ELIGIBLE",
            explanation="User meets all mandatory requirements: Verified Matric completed, Marketing Management N5 certificate held, no prior experience required.",
            satisfied_requirements='["Matric Certificate (Verified)", "Marketing Management N5 (Verified)", "No experience required"]',
            missing_requirements='[]',
            uncertain_points='[]'
        )
        db.add(dec_1)

        # Vacancy 2: Not Eligible - Senior Marketing Manager
        desc_2 = (
            "Senior Brand Manager wanted. Requirements: BCom Honours Marketing, minimum 5 years commercial brand management experience."
        )
        fp_2 = hashlib.sha256(("Senior Brand Manager" + "FMCG Brands" + "CPT").encode()).hexdigest()
        v2 = Vacancy(
            title="Senior Brand Manager",
            employer="Premier FMCG Brands",
            location="Cape Town",
            province="Western Cape",
            salary="R45,000 - R55,000 per month",
            employment_type="Full-time",
            qualification_requirements="BCom Honours in Marketing",
            experience_requirements="Minimum 5 years brand management experience",
            skills_requirements="Strategic Planning, P&L Management",
            drivers_licence_required="Code 08 (B)",
            citizenship_required="South African Citizen",
            required_documents="CV, Certified Copies of Degrees",
            application_method="email",
            application_email="jobs@fmcgbrands.co.za",
            closing_date="2026-11-30",
            reference_number="FMCG-BM-99",
            description=desc_2,
            source_url="https://fmcgbrands.co.za/careers/senior-brand-manager",
            vacancy_fingerprint=fp_2
        )
        db.add(v2)
        db.flush()

        dec_2 = EligibilityDecision(
            vacancy_id=v2.id,
            classification="NOT_ELIGIBLE",
            explanation="User does not satisfy mandatory requirement of 5 years prior experience and BCom Honours degree.",
            satisfied_requirements='["Matric completed"]',
            missing_requirements='["5 years work experience", "BCom Honours Degree"]',
            uncertain_points='[]'
        )
        db.add(dec_2)

        # Vacancy 3: Uncertain - Junior Administrative Clerk
        desc_3 = (
            "Junior Administrative Clerk required for regional municipal office in Kimberley, Northern Cape. "
            "Must have Grade 12. Valid driver's licence preferred."
        )
        fp_3 = hashlib.sha256(("Junior Admin Clerk" + "Northern Cape Dept" + "KIM").encode()).hexdigest()
        v3 = Vacancy(
            title="Junior Administrative Clerk",
            employer="Department of Provincial Administration",
            location="Kimberley",
            province="Northern Cape",
            salary="R12,000 per month",
            employment_type="Full-time",
            qualification_requirements="Grade 12 / Matric",
            experience_requirements="Entry level",
            skills_requirements="Filing, MS Word, Data Entry",
            drivers_licence_required="Code B preferred",
            citizenship_required="South African Citizen",
            required_documents="Z83 Form, CV, Certified ID, Matric Certificate",
            application_method="email",
            application_email="recruitment@northerncape.gov.za",
            closing_date="2026-12-05",
            reference_number="NC-ADM-2026/88",
            description=desc_3,
            source_url="https://govpage.co.za/northern-cape-admin-clerk",
            vacancy_fingerprint=fp_3
        )
        db.add(v3)
        db.flush()

        dec_3 = EligibilityDecision(
            vacancy_id=v3.id,
            classification="UNCERTAIN",
            explanation="User has Matric (satisfied), but driver's licence status in profile is unverified / None.",
            satisfied_requirements='["Matric (Grade 12)"]',
            missing_requirements='[]',
            uncertain_points='["Valid driver\'s licence status"]'
        )
        db.add(dec_3)

        # Create a sample submitted application for Vacancy 1
        app = Application(
            vacancy_id=v1.id,
            status="SUBMITTED",
            application_method="email",
            notes="Submitted tailored CV and cover letter matching N5 Marketing qualification."
        )
        db.add(app)
        db.flush()

        sub = EmailSubmission(
            application_id=app.id,
            recipient_email=v1.application_email,
            subject=f"Application: {v1.title} - Ref: {v1.reference_number}",
            gmail_message_id="mock_msg_id_187654321",
            attachments='["Tailored_CV_Marketing_Intern.pdf", "Cover_Letter_RetailGroupSA.pdf", "Matric_Certificate.pdf", "N5_Certificate.pdf"]',
            status="SENT"
        )
        db.add(sub)

        log = ApplicationLog(
            application_id=app.id,
            level="INFO",
            message=f"Application email successfully dispatched via Gmail API to {v1.application_email}"
        )
        db.add(log)

        db.commit()


# Ensure tables exist at startup
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Ensure document storage directory exists
    storage_dir = Path(settings.DOCUMENT_STORAGE_PATH)
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Initialize profile and seed initial data
    db = SessionLocal()
    try:
        get_or_create_initial_profile(db)
        seed_sample_data(db)
    finally:
        db.close()

    yield

    # Shutdown logic (if any)


app = FastAPI(
    title="BOB — Autonomous AI Job Application Agent",
    description="Backend API powering Bob, the South African job hunting & application desktop agent.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for desktop frontend (Electron / Vite localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(vacancies_router, prefix="/api")
app.include_router(applications_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(settings_router, prefix="/api")


@app.get("/")
def root():
    return {
        "agent": "BOB",
        "role": "Autonomous South African Job Application Agent",
        "status": "Online",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

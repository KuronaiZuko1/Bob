import json
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.models.vacancy import Vacancy, EligibilityDecision
from backend.app.models.profile import Profile
from backend.app.schemas.vacancy import VacancyOut, VacancyCreate
from backend.app.services.ai_provider import evaluate_eligibility_ai
from backend.app.services.discovery.pipeline import JobDiscoveryPipeline

router = APIRouter(prefix="/vacancies", tags=["Vacancies"])


@router.get("/sources")
def get_discovery_sources():
    """Retrieve metadata about all active South African job source adapters."""
    pipeline = JobDiscoveryPipeline()
    return {"sources": pipeline.get_sources()}


@router.post("/discover")
async def trigger_job_discovery(
    source: Optional[str] = Query(None, description="Optional specific adapter name filter"),
    db: Session = Depends(get_db)
):
    """
    Trigger the South African job discovery engine.
    Scrapes/fetches vacancies, performs 3-point deduplication, persists new posts,
    and automatically runs AI eligibility evaluations against the applicant profile.
    """
    pipeline = JobDiscoveryPipeline()
    stats = await pipeline.run(db, source_name=source)
    return {
        "status": "success",
        "message": f"Job discovery completed. Added {stats['new_vacancies_added']} new vacancies ({stats['evaluated_eligible']} eligible).",
        "stats": stats
    }


@router.get("", response_model=List[VacancyOut])
def list_vacancies(
    search: Optional[str] = None,
    province: Optional[str] = None,
    eligibility: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Vacancy)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Vacancy.title.ilike(search_filter)) |
            (Vacancy.employer.ilike(search_filter)) |
            (Vacancy.description.ilike(search_filter))
        )

    if province:
        query = query.filter(Vacancy.province.ilike(f"%{province}%"))

    if eligibility:
        query = query.join(Vacancy.eligibility_decision).filter(
            EligibilityDecision.classification == eligibility.upper()
        )

    return query.order_by(Vacancy.discovered_at.desc()).limit(limit).all()


@router.get("/{vacancy_id}", response_model=VacancyOut)
def get_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy


@router.post("/{vacancy_id}/evaluate", response_model=VacancyOut)
async def evaluate_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    """
    Run the AI/Deterministic Eligibility Engine on a vacancy against verified applicant profile.
    Saves and updates the structured EligibilityDecision record.
    """
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Applicant profile not found")

    # Serialize profile for evaluation
    profile_data = {
        "full_name": profile.full_legal_name,
        "nationality": "South African",
        "province": profile.province,
        "city": profile.town_city,
        "drivers_licence": profile.drivers_licence,
        "qualifications": [{"name": q.qualification_name, "institution": q.institution, "year": q.end_year} for q in profile.qualifications],
        "skills": [{"name": s.name, "proficiency": s.proficiency} for s in profile.skills],
        "experiences": [{"title": e.job_title, "employer": e.employer, "duration": f"{e.start_date} to {e.end_date}"} for e in profile.experiences]
    }

    vacancy_data = {
        "title": vacancy.title,
        "employer": vacancy.employer,
        "location": vacancy.location,
        "qualification_requirements": vacancy.qualification_requirements,
        "experience_requirements": vacancy.experience_requirements,
        "skills_requirements": vacancy.skills_requirements,
        "drivers_licence_required": vacancy.drivers_licence_required,
        "description": vacancy.description
    }

    decision = await evaluate_eligibility_ai(profile_data, vacancy_data)

    # Persist or update decision
    if vacancy.eligibility_decision:
        vacancy.eligibility_decision.classification = decision.classification
        vacancy.eligibility_decision.explanation = decision.explanation
        vacancy.eligibility_decision.satisfied_requirements = json.dumps(decision.satisfied_requirements)
        vacancy.eligibility_decision.missing_requirements = json.dumps(decision.missing_mandatory_requirements)
        vacancy.eligibility_decision.uncertain_points = json.dumps(decision.uncertain_points)
        vacancy.eligibility_decision.evaluated_at = datetime.now(timezone.utc)
    else:
        new_dec = EligibilityDecision(
            vacancy_id=vacancy.id,
            classification=decision.classification,
            explanation=decision.explanation,
            satisfied_requirements=json.dumps(decision.satisfied_requirements),
            missing_requirements=json.dumps(decision.missing_mandatory_requirements),
            uncertain_points=json.dumps(decision.uncertain_points),
            evaluated_at=datetime.now(timezone.utc)
        )
        db.add(new_dec)

    db.commit()
    db.refresh(vacancy)
    return vacancy

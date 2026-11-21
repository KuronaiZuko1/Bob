"""
BOB Job Discovery Pipeline Coordinator
Coordinates multiple South African source adapters, deduplicates posts,
persists verified vacancies to SQLite, and automatically evaluates eligibility using Phase 3 AI engine.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.models.vacancy import Vacancy, EligibilityDecision
from backend.app.models.profile import Profile
from backend.app.models.application import ApplicationLog
from backend.app.models.settings import SearchHistory
from backend.app.services.discovery.base import BaseSourceAdapter, RawVacancy
from backend.app.services.discovery.adapters import (
    DPSAGovAdapter,
    SAEntryLevelAdapter,
    CorporateRetailAdapter
)
from backend.app.services.ai_provider import evaluate_eligibility_ai

logger = logging.getLogger(__name__)


class JobDiscoveryPipeline:
    """Orchestrates job scraping, deduplication, database persistence and AI evaluation."""

    def __init__(self, adapters: Optional[List[BaseSourceAdapter]] = None):
        self.adapters: List[BaseSourceAdapter] = adapters or [
            DPSAGovAdapter(),
            SAEntryLevelAdapter(),
            CorporateRetailAdapter()
        ]

    def get_sources(self) -> List[Dict[str, Any]]:
        """List registered source adapters and metadata."""
        return [adapter.get_info() for adapter in self.adapters]

    async def run(self, db: Session, source_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute discovery across active adapters.
        Deduplicates by fingerprint, source URL, and reference number.
        Runs immediate AI eligibility evaluation on newly discovered vacancies.
        """
        target_adapters = self.adapters
        if source_name:
            target_adapters = [a for a in self.adapters if a.name.lower() == source_name.lower()]
            if not target_adapters:
                target_adapters = [a for a in self.adapters if source_name.lower() in a.name.lower()]

        stats = {
            "sources_scanned": len(target_adapters),
            "discovered_total": 0,
            "new_vacancies_added": 0,
            "duplicate_vacancies_skipped": 0,
            "evaluated_eligible": 0,
            "evaluated_not_eligible": 0,
            "evaluated_uncertain": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Fetch profile facts for automatic eligibility evaluation
        profile = db.query(Profile).first()
        profile_data = {}
        if profile:
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

        for adapter in target_adapters:
            try:
                raw_vacancies: List[RawVacancy] = await adapter.fetch_vacancies()
                stats["discovered_total"] += len(raw_vacancies)
                adapter_new = 0

                for raw in raw_vacancies:
                    fingerprint = raw.compute_fingerprint()

                    # Deduplication check 1: Exact SHA-256 fingerprint
                    existing = db.query(Vacancy).filter(Vacancy.vacancy_fingerprint == fingerprint).first()
                    if existing:
                        stats["duplicate_vacancies_skipped"] += 1
                        continue

                    # Deduplication check 2: Source URL
                    if raw.source_url:
                        existing_url = db.query(Vacancy).filter(Vacancy.source_url == raw.source_url).first()
                        if existing_url:
                            stats["duplicate_vacancies_skipped"] += 1
                            continue

                    # Deduplication check 3: Reference Number (if non-empty)
                    if raw.reference_number:
                        existing_ref = db.query(Vacancy).filter(
                            Vacancy.reference_number == raw.reference_number,
                            Vacancy.employer == raw.employer
                        ).first()
                        if existing_ref:
                            stats["duplicate_vacancies_skipped"] += 1
                            continue

                    # New Vacancy: persist to database
                    vacancy = Vacancy(
                        title=raw.title,
                        employer=raw.employer,
                        location=raw.location,
                        province=raw.province,
                        salary=raw.salary,
                        employment_type=raw.employment_type,
                        qualification_requirements=raw.qualification_requirements,
                        experience_requirements=raw.experience_requirements,
                        skills_requirements=raw.skills_requirements,
                        age_requirements=raw.age_requirements,
                        drivers_licence_required=raw.drivers_licence_required,
                        citizenship_required=raw.citizenship_required,
                        required_documents=raw.required_documents,
                        application_method=raw.application_method,
                        application_email=raw.application_email,
                        application_url=raw.application_url,
                        closing_date=raw.closing_date,
                        reference_number=raw.reference_number,
                        description=raw.description,
                        source_url=raw.source_url,
                        vacancy_fingerprint=fingerprint,
                        is_active=True,
                        discovered_at=raw.discovered_at
                    )
                    db.add(vacancy)
                    db.flush()  # assign vacancy.id

                    # Run Phase 3 AI / Deterministic Eligibility Engine
                    if profile_data:
                        vac_eval_payload = {
                            "title": vacancy.title,
                            "employer": vacancy.employer,
                            "location": vacancy.location,
                            "qualification_requirements": vacancy.qualification_requirements,
                            "experience_requirements": vacancy.experience_requirements,
                            "skills_requirements": vacancy.skills_requirements,
                            "drivers_licence_required": vacancy.drivers_licence_required,
                            "description": vacancy.description
                        }
                        decision = await evaluate_eligibility_ai(profile_data, vac_eval_payload)

                        elig_record = EligibilityDecision(
                            vacancy_id=vacancy.id,
                            classification=decision.classification,
                            explanation=decision.explanation,
                            satisfied_requirements=json.dumps(decision.satisfied_requirements),
                            missing_requirements=json.dumps(decision.missing_mandatory_requirements),
                            uncertain_points=json.dumps(decision.uncertain_points),
                            evaluated_at=datetime.now(timezone.utc)
                        )
                        db.add(elig_record)

                        if decision.classification == "ELIGIBLE":
                            stats["evaluated_eligible"] += 1
                        elif decision.classification == "NOT_ELIGIBLE":
                            stats["evaluated_not_eligible"] += 1
                        else:
                            stats["evaluated_uncertain"] += 1

                    stats["new_vacancies_added"] += 1
                    adapter_new += 1

                # Record Search History entry
                search_log = SearchHistory(
                    source_name=adapter.name,
                    search_query="All open posts",
                    vacancies_found=len(raw_vacancies),
                    status="COMPLETED"
                )
                db.add(search_log)

            except Exception as adapter_err:
                logger.error("Error executing adapter %s: %s", adapter.name, str(adapter_err))
                err_log = SearchHistory(
                    source_name=adapter.name,
                    search_query="All open posts",
                    vacancies_found=0,
                    status="FAILED",
                    error_message=str(adapter_err)
                )
                db.add(err_log)

        # Audit application log
        log = ApplicationLog(
            level="INFO",
            message=f"Job Discovery completed: {stats['new_vacancies_added']} new vacancies added ({stats['evaluated_eligible']} eligible), {stats['duplicate_vacancies_skipped']} duplicates skipped."
        )
        db.add(log)
        db.commit()

        return stats

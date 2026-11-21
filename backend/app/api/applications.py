"""
BOB Applications API — Phase 5
Endpoints for document generation, application record management, and file download.
"""
import os
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.application import Application, ApplicationLog, EmailSubmission, WebsiteSubmission
from backend.app.models.profile import Profile
from backend.app.models.vacancy import Vacancy
from backend.app.schemas.application import ApplicationOut
from backend.app.services.document_generator import generate_tailored_cv, generate_tailored_cover_letter
from backend.app.services.gmail_service import send_application_email
from backend.app.services.website_applicator import apply_via_website
from backend.app.services.telegram_bot import send_telegram_notification

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=List[ApplicationOut])
def list_applications(
    status: Optional[str] = None,
    method: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve list of job applications submitted or pending."""
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status.upper())
    if method:
        query = query.filter(Application.application_method == method.lower())
    return query.order_by(Application.created_at.desc()).limit(limit).all()


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(application_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed record of a single application."""
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        raise HTTPException(status_code=404, detail="Application record not found")
    return app_record


@router.post("/generate-documents/{vacancy_id}", response_model=ApplicationOut)
def generate_application_documents(vacancy_id: int, db: Session = Depends(get_db)):
    """
    Generate tailored CV and cover letter for an eligible vacancy.
    Creates or returns an existing Application record for the vacancy.
    Only strictly verified profile facts are used — no fabrication.
    """
    # Load vacancy
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    # Check eligibility
    elig_classification = (
        vacancy.eligibility_decision.classification
        if vacancy.eligibility_decision
        else "UNCERTAIN"
    )
    if elig_classification == "NOT_ELIGIBLE":
        reason = (
            vacancy.eligibility_decision.explanation
            if vacancy.eligibility_decision
            else "Mandatory criteria not met"
        )
        raise HTTPException(
            status_code=422,
            detail=f"Cannot generate documents for a NOT_ELIGIBLE vacancy. Reason: {reason}"
        )

    # Load primary profile
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No user profile found. Please complete your profile first.")

    # Determine application method
    application_method = "email" if vacancy.application_email else "website"

    # Check for existing application record for this vacancy
    existing = db.query(Application).filter(Application.vacancy_id == vacancy_id).first()
    if existing and existing.tailored_cv_path and Path(existing.tailored_cv_path).exists():
        return existing

    # Generate documents
    try:
        docx_path, pdf_path = generate_tailored_cv(profile, vacancy)
        cover_path = generate_tailored_cover_letter(profile, vacancy)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")

    # Create or update application record
    if existing:
        existing.tailored_cv_path = pdf_path
        existing.cover_letter_path = cover_path
        existing.updated_at = datetime.now(timezone.utc)
        app_record = existing
    else:
        app_record = Application(
            vacancy_id=vacancy.id,
            profile_id=profile.id,
            status="PENDING",
            application_method=application_method,
            tailored_cv_path=pdf_path,
            cover_letter_path=cover_path,
            notes=f"Documents generated. CV (DOCX): {docx_path}"
        )
        db.add(app_record)

    db.flush()

    # Log the generation event
    log_entry = ApplicationLog(
        application_id=app_record.id,
        level="INFO",
        message=f"Generated tailored CV and cover letter for vacancy: {vacancy.title} at {vacancy.employer}"
    )
    db.add(log_entry)
    db.commit()
    db.refresh(app_record)

    return app_record


@router.get("/{application_id}/download-cv")
def download_cv(application_id: int, fmt: str = Query("pdf"), db: Session = Depends(get_db)):
    """
    Download the generated CV for an application.
    Use fmt=pdf (default) or fmt=docx.
    """
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        raise HTTPException(status_code=404, detail="Application not found")

    cv_path = app_record.tailored_cv_path
    if not cv_path:
        raise HTTPException(status_code=404, detail="No CV generated for this application yet")

    # Support DOCX fallback
    if fmt == "docx":
        docx_path = cv_path.replace(".pdf", ".docx")
        if Path(docx_path).exists():
            cv_path = docx_path

    if not Path(cv_path).exists():
        raise HTTPException(status_code=404, detail=f"CV file not found at path: {cv_path}")

    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if cv_path.endswith(".docx") else "application/pdf"
    filename = Path(cv_path).name
    return FileResponse(cv_path, media_type=media_type, filename=filename)


@router.get("/{application_id}/download-cover-letter")
def download_cover_letter(application_id: int, db: Session = Depends(get_db)):
    """Download the generated cover letter PDF for an application."""
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        raise HTTPException(status_code=404, detail="Application not found")

    cl_path = app_record.cover_letter_path
    if not cl_path:
        raise HTTPException(status_code=404, detail="No cover letter generated for this application yet")

    if not Path(cl_path).exists():
        raise HTTPException(status_code=404, detail=f"Cover letter file not found at path: {cl_path}")

    return FileResponse(cl_path, media_type="application/pdf", filename=Path(cl_path).name)


@router.post("/{application_id}/submit", response_model=ApplicationOut)
async def submit_application(application_id: int, db: Session = Depends(get_db)):
    """
    Dispatch an application via Email (Gmail API) or Web Portal (Playwright).
    Respects TEST_MODE setting and records complete audit logs and evidence.
    """
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        raise HTTPException(status_code=404, detail="Application record not found")

    profile = db.query(Profile).filter(Profile.id == app_record.profile_id).first() or db.query(Profile).first()
    vacancy = db.query(Vacancy).filter(Vacancy.id == app_record.vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Associated vacancy not found")

    # If documents not generated yet, generate them first
    if not app_record.tailored_cv_path or not Path(app_record.tailored_cv_path).exists():
        docx_path, pdf_path = generate_tailored_cv(profile, vacancy)
        cl_path = generate_tailored_cover_letter(profile, vacancy)
        app_record.tailored_cv_path = pdf_path
        app_record.cover_letter_path = cl_path

    # Dispatch based on application method
    method = (app_record.application_method or vacancy.application_method or "email").lower()
    submission_success = False

    if method == "email" or vacancy.application_email:
        res = send_application_email(profile, vacancy, app_record)
        app_record.status = res.get("status", "SUBMITTED")
        app_record.submitted_at = datetime.now(timezone.utc)
        sub_record = db.query(EmailSubmission).filter(EmailSubmission.application_id == app_record.id).first()
        if not sub_record:
            sub_record = EmailSubmission(
                application_id=app_record.id,
                recipient_email=vacancy.application_email or "careers@example.co.za",
                subject=res.get("subject", f"Application for {vacancy.title}"),
                gmail_message_id=res.get("message_id"),
                status=res.get("status", "SENT")
            )
            db.add(sub_record)
        else:
            sub_record.gmail_message_id = res.get("message_id")
            sub_record.status = res.get("status", "SENT")
        submission_success = True
        log_msg = f"Email application dispatched to {vacancy.application_email} (Result: {res.get('status')})"

    elif method == "website" or vacancy.application_url:
        res = await apply_via_website(profile, vacancy, app_record)
        app_record.status = res.get("status", "SUBMITTED")
        app_record.submitted_at = datetime.now(timezone.utc)
        web_record = db.query(WebsiteSubmission).filter(WebsiteSubmission.application_id == app_record.id).first()
        if not web_record:
            web_record = WebsiteSubmission(
                application_id=app_record.id,
                portal_url=res.get("portal_url", vacancy.application_url or vacancy.source_url),
                submission_reference=res.get("submission_reference"),
                screenshot_path=res.get("screenshot_path"),
                status=res.get("status", "SUBMITTED")
            )
            db.add(web_record)
        else:
            web_record.submission_reference = res.get("submission_reference")
            web_record.screenshot_path = res.get("screenshot_path")
            web_record.status = res.get("status", "SUBMITTED")
        submission_success = (res.get("status") in ["SUBMITTED", "SUBMITTED_TEST_MODE"])
        log_msg = f"Website application submitted to {web_record.portal_url} (Ref: {res.get('submission_reference')})"

    else:
        app_record.status = "REQUIRES_ATTENTION"
        log_msg = "Application has no known email or portal URL."

    # Record log entry
    db.add(ApplicationLog(
        application_id=app_record.id,
        level="INFO" if submission_success else "WARNING",
        message=log_msg
    ))
    db.commit()
    db.refresh(app_record)

    # Notify via Telegram
    try:
        tg_text = (
            f"📬 <b>Application Update:</b> {vacancy.title} at {vacancy.employer}\n"
            f"Status: <b>{app_record.status}</b> via {method.upper()}\n"
            f"Mode: {'Test Mode (Simulated)' if settings.TEST_MODE else 'Live'}"
        )
        await send_telegram_notification(tg_text)
    except Exception:
        pass

    return app_record


@router.delete("/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    """Delete an application record (does not delete generated files)."""
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app_record)
    db.commit()
    return {"message": "Application record deleted"}

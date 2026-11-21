from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.profile import Profile
from backend.app.models.vacancy import Vacancy, EligibilityDecision
from backend.app.services.document_generator import (
    generate_tailored_cv,
    generate_tailored_cover_letter,
)

client = TestClient(app)


def test_cv_and_cover_letter_generation_unit():
    db = SessionLocal()
    try:
        profile = db.query(Profile).first()
        assert profile is not None

        # Fetch an eligible or sample vacancy
        vacancy = db.query(Vacancy).first()
        assert vacancy is not None

        # 1. Generate CV
        docx_path, pdf_path = generate_tailored_cv(profile, vacancy)
        assert Path(docx_path).exists()
        assert Path(pdf_path).exists()
        assert Path(docx_path).stat().st_size > 0
        assert Path(pdf_path).stat().st_size > 0

        # Verify truthful content
        assert "CV" in Path(docx_path).name

        # 2. Generate Cover Letter
        cl_path = generate_tailored_cover_letter(profile, vacancy)
        assert Path(cl_path).exists()
        assert Path(cl_path).stat().st_size > 0
        assert "Cover_Letter" in Path(cl_path).name
    finally:
        db.close()


def test_api_generate_and_download_documents():
    db = SessionLocal()
    try:
        # Find an ELIGIBLE vacancy (such as Vacancy 1 from seed data)
        vac = (
            db.query(Vacancy)
            .join(EligibilityDecision)
            .filter(EligibilityDecision.classification == "ELIGIBLE")
            .first()
        )
        assert vac is not None, "Seeded eligible vacancy should exist"
        vac_id = vac.id
    finally:
        db.close()

    # 1. API: Generate Documents
    response = client.post(f"/api/applications/generate-documents/{vac_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["vacancy_id"] == vac_id
    assert data["status"] in ["PENDING", "SUBMITTED"]
    assert data["tailored_cv_path"] is not None
    assert data["cover_letter_path"] is not None
    app_id = data["id"]

    # 2. API: Download CV (PDF)
    res_cv_pdf = client.get(f"/api/applications/{app_id}/download-cv?fmt=pdf")
    assert res_cv_pdf.status_code == 200
    assert "application/pdf" in res_cv_pdf.headers["content-type"]
    assert len(res_cv_pdf.content) > 0

    # 3. API: Download CV (DOCX)
    res_cv_docx = client.get(f"/api/applications/{app_id}/download-cv?fmt=docx")
    assert res_cv_docx.status_code == 200
    assert len(res_cv_docx.content) > 0

    # 4. API: Download Cover Letter
    res_cl = client.get(f"/api/applications/{app_id}/download-cover-letter")
    assert res_cl.status_code == 200
    assert "application/pdf" in res_cl.headers["content-type"]
    assert len(res_cl.content) > 0


def test_reject_generate_documents_for_ineligible_vacancy():
    db = SessionLocal()
    try:
        # Find a NOT_ELIGIBLE vacancy (such as Vacancy 2 from seed data)
        ineligible_vac = (
            db.query(Vacancy)
            .join(EligibilityDecision)
            .filter(EligibilityDecision.classification == "NOT_ELIGIBLE")
            .first()
        )
        assert ineligible_vac is not None, "Seeded not eligible vacancy should exist"
        vac_id = ineligible_vac.id
    finally:
        db.close()

    response = client.post(f"/api/applications/generate-documents/{vac_id}")
    assert response.status_code == 422
    assert "Cannot generate documents for a NOT_ELIGIBLE vacancy" in response.json()["detail"]

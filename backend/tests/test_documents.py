import io
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.vault import encrypt_and_store, retrieve_and_decrypt, delete_stored_file
from backend.app.services.document_processor import (
    classify_document,
    extract_text,
    mask_sa_id_numbers
)

client = TestClient(app)


def test_vault_encryption_decryption_lifecycle():
    """Test that arbitrary file bytes are properly encrypted on disk and decrypted accurately."""
    payload = b"South African National Senior Certificate - Matric 2022"
    filename = "matric_test.txt"

    stored_name, path, size, checksum = encrypt_and_store(payload, filename)

    assert stored_name.endswith(".txt.enc")
    assert size == len(payload)
    assert len(checksum) == 64  # SHA-256 length

    # Retrieve and verify decrypted bytes
    decrypted = retrieve_and_decrypt(stored_name)
    assert decrypted == payload

    # Clean up
    deleted = delete_stored_file(stored_name)
    assert deleted is True


def test_document_classification():
    """Test intelligent classification of South African job seeker documents."""
    assert classify_document("National Senior Certificate Umalusi Grade 12", "cert.pdf") == "matric"
    assert classify_document("National Certificate Marketing Management N5 TVET", "doc.pdf") == "certificate"
    assert classify_document("Republic of South Africa Identity Document ID No 0101015000085", "id.pdf") == "id_document"
    assert classify_document("Curriculum Vitae Personal Profile Work Experience", "cv.docx") == "cv"
    assert classify_document("Municipal Account Rates and Taxes Proof of Residence", "res.pdf") == "proof_of_residence"
    assert classify_document("Random miscellaneous document", "notes.txt") == "other"


def test_mask_sa_id():
    """Test privacy masking of South African ID numbers."""
    raw = "Applicant ID is 9901015000085 for verification."
    masked = mask_sa_id_numbers(raw)
    assert "9901015000085" not in masked
    assert "Applicant ID is" in masked


def test_upload_and_preview_document():
    """Test the complete /api/documents upload, preview, and delete flow."""
    test_content = b"National Senior Certificate\nSubject: Mathematics Level 5\nCandidate: 0101015000085"
    file = io.BytesIO(test_content)

    # 1. Upload
    response = client.post(
        "/api/documents/upload",
        files={"file": ("matric_certificate.txt", file, "text/plain")},
        data={"category": "matric"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "matric_certificate.txt"
    assert data["document_category"] == "matric"
    assert data["is_encrypted"] is True
    doc_id = data["id"]

    # 2. Preview / Download (decrypted)
    preview_res = client.get(f"/api/documents/{doc_id}/preview")
    assert preview_res.status_code == 200
    assert preview_res.content == test_content

    # 3. Toggle verification
    verify_res = client.post(f"/api/documents/{doc_id}/verify")
    assert verify_res.status_code == 200
    assert verify_res.json()["is_verified"] is True

    # 4. List documents
    list_res = client.get("/api/documents")
    assert list_res.status_code == 200
    assert any(d["id"] == doc_id for d in list_res.json())

    # 5. Delete document
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

    # Verify 404 after deletion
    get_res = client.get(f"/api/documents/{doc_id}")
    assert get_res.status_code == 404

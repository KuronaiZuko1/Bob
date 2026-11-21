import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.document import Document
from backend.app.models.profile import Profile, Qualification
from backend.app.models.application import ApplicationLog
from backend.app.schemas.document import DocumentOut
from backend.app.services.vault import encrypt_and_store, retrieve_and_decrypt, delete_stored_file
from backend.app.services.document_processor import extract_text, classify_document

router = APIRouter(prefix="/documents", tags=["Documents"])

SUPPORTED_CATEGORIES = [
    "id_document",
    "matric",
    "certificate",
    "transcript",
    "cv",
    "cover_letter",
    "proof_of_residence",
    "drivers_licence",
    "other"
]


@router.get("", response_model=List[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    """Retrieve list of documents in the secure vault."""
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.get("/categories")
def get_document_categories():
    """Retrieve recognized South African employment document categories."""
    return {"categories": SUPPORTED_CATEGORIES}


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form("other"),
    db: Session = Depends(get_db)
):
    """
    Securely upload, inspect, auto-classify, encrypt, and store a document in the vault.
    Accepts PDF, DOCX, JPG, PNG.
    """
    # 1. Read file bytes
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size ({settings.MAX_UPLOAD_MB}MB)")

    filename = file.filename or "uploaded_document"
    mime_type = file.content_type or "application/octet-stream"

    # 2. Extract text for analysis & eligibility engine
    extracted_text = extract_text(file_bytes, filename, mime_type)

    # 3. Classify document
    detected_category = classify_document(extracted_text, filename, user_hint=category)

    # 4. Encrypt and store file payload
    try:
        stored_filename, file_path, file_size, checksum = encrypt_and_store(file_bytes, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to encrypt and store document: {str(e)}")

    # 5. Associate with primary profile if available
    profile = db.query(Profile).first()
    profile_id = profile.id if profile else None

    # 6. Save document model to database
    doc = Document(
        profile_id=profile_id,
        original_filename=filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_type=mime_type,
        file_size_bytes=file_size,
        document_category=detected_category,
        extracted_text=extracted_text,
        is_verified=False,
        is_encrypted=True,
        checksum=checksum
    )
    db.add(doc)

    # 7. Add audit log
    log = ApplicationLog(
        level="INFO",
        message=f"Document uploaded: {filename} classified as {detected_category}. Encrypted at rest."
    )
    db.add(log)
    db.commit()
    db.refresh(doc)

    return doc


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Retrieve document metadata."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/preview")
def preview_document(document_id: int, db: Session = Depends(get_db)):
    """Decrypt and return document for viewing/download."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        decrypted_bytes = retrieve_and_decrypt(doc.stored_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decrypt document: {str(e)}")

    return StreamingResponse(
        io.BytesIO(decrypted_bytes),
        media_type=doc.file_type,
        headers={"Content-Disposition": f"inline; filename=\"{doc.original_filename}\""}
    )


@router.post("/{document_id}/verify", response_model=DocumentOut)
def verify_document(document_id: int, db: Session = Depends(get_db)):
    """Toggle verified status of a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.is_verified = not doc.is_verified
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Securely delete document from disk and database."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Secure file wipe
    delete_stored_file(doc.stored_filename)

    db.delete(doc)

    log = ApplicationLog(
        level="INFO",
        message=f"Document deleted: {doc.original_filename} (id: {doc.id})"
    )
    db.add(log)
    db.commit()

    return {"status": "deleted", "id": document_id}

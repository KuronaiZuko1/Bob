"""
BOB Document Processing & Classification Service
Extracts text from PDF, DOCX, and image files.
Categorizes documents into standard South African job application types.
"""
import io
import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import pypdf
import docx
from PIL import Image

# South African 13-digit ID pattern: YYMMDD SSSS C A Z (or any 13-digit sequence in text)
SA_ID_REGEX = re.compile(r"\b\d{13}\b")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract clean text content from PDF binary using pypdf."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    text_parts = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_parts.append(extracted)
    return "\n".join(text_parts).strip()


def extract_text_from_docx(docx_bytes: bytes) -> str:
    """Extract clean text content from DOCX binary."""
    doc = docx.Document(io.BytesIO(docx_bytes))
    text_parts = [para.text for para in doc.paragraphs if para.text]
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                text_parts.append(row_text)
    return "\n".join(text_parts).strip()


def extract_image_info(img_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """Inspect image and extract metadata."""
    try:
        image = Image.open(io.BytesIO(img_bytes))
        info = {
            "format": image.format,
            "dimensions": f"{image.width}x{image.height}",
            "mode": image.mode
        }
        return f"[Image document: {image.format} {image.width}x{image.height}]", info
    except Exception as e:
        return f"[Image document: unreadable image ({e})]", {}


def extract_text(file_bytes: bytes, filename: str, mime_type: str) -> str:
    """Extract text based on file extension and mime type."""
    ext = Path(filename).suffix.lower()

    if ext == ".pdf" or "pdf" in mime_type:
        try:
            return extract_text_from_pdf(file_bytes)
        except Exception as e:
            return f"[PDF parsing error: {e}]"

    elif ext in [".docx", ".doc"] or "word" in mime_type or "officedocument" in mime_type:
        try:
            return extract_text_from_docx(file_bytes)
        except Exception as e:
            return f"[DOCX parsing error: {e}]"

    elif ext in [".png", ".jpg", ".jpeg", ".webp"] or "image" in mime_type:
        text, _ = extract_image_info(file_bytes)
        return text

    elif ext in [".txt", ".text"]:
        try:
            return file_bytes.decode("utf-8", errors="replace")
        except Exception:
            return ""

    return ""


def classify_document(text: str, filename: str, user_hint: Optional[str] = None) -> str:
    """
    Classify document type using keywords, regex, filename and optional user selection.
    Recognized categories:
      - id_document
      - matric
      - certificate
      - transcript
      - cv
      - cover_letter
      - proof_of_residence
      - drivers_licence
      - other
    """
    if user_hint and user_hint != "other":
        return user_hint

    combined = f"{filename} {text}".upper()

    # South African ID
    if "REPUBLIC OF SOUTH AFRICA" in combined and ("IDENTITY" in combined or "NATIONAL IDENTITY" in combined):
        return "id_document"
    if "SOUTH AFRICAN ID" in combined or "ID DOCUMENT" in combined:
        return "id_document"
    if SA_ID_REGEX.search(text):
        return "id_document"

    # Matric Certificate
    if any(k in combined for k in ["NATIONAL SENIOR CERTIFICATE", "SENIOR CERTIFICATE", "MATRIC", "UMALUSI", "GRADE 12"]):
        return "matric"

    # College / N-Level / Marketing Management Certificate
    if any(k in combined for k in [
        "NATIONAL CERTIFICATE", "MARKETING MANAGEMENT", "N5 CERTIFICATE", "N4 CERTIFICATE",
        "N6 CERTIFICATE", "TVET", "DHET", "DIPLOMA", "DEGREE", "HIGHER CERTIFICATE"
    ]):
        return "certificate"

    # Academic Transcript
    if any(k in combined for k in ["ACADEMIC RECORD", "STATEMENT OF RESULTS", "TRANSCRIPT", "ACADEMIC TRANSCRIPT"]):
        return "transcript"

    # CV / Resume
    if any(k in combined for k in ["CURRICULUM VITAE", "RESUME", "CAREER PROFILE", "WORK EXPERIENCE", "PERSONAL DETAILS"]):
        return "cv"

    # Cover Letter
    if any(k in combined for k in ["COVER LETTER", "APPLICATION FOR THE POSITION", "DEAR HIRING", "DEAR SIR/MADAM"]):
        return "cover_letter"

    # Proof of Residence
    if any(k in combined for k in ["PROOF OF RESIDENCE", "UTILITY BILL", "MUNICIPAL ACCOUNT", "RATES AND TAXES", "RESIDENTIAL ADDRESS"]):
        return "proof_of_residence"

    # Driver's Licence
    if any(k in combined for k in ["DRIVING LICENCE", "DRIVER'S LICENCE", "CODE B", "CODE EB", "CODE C", "CODE EC"]):
        return "drivers_licence"

    return "other"


def mask_sa_id_numbers(text: str) -> str:
    """Mask any detected 13-digit SA ID numbers for privacy (e.g. **********085)."""
    return SA_ID_REGEX.sub(lambda m: "**********" + m.group(0)[-3:], text)

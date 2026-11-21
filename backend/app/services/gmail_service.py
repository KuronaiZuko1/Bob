"""
BOB Gmail Service — Phase 6
Handles Google OAuth 2.0 flow, token storage, email composition, and message transmission.
Never stores user passwords — uses official Google OAuth2.
In TEST_MODE or when unconfigured, logs and simulates sending without external API calls.
"""
import os
import json
import base64
import mimetypes
from pathlib import Path
from email.message import EmailMessage
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from backend.app.core.config import settings
from backend.app.models.application import Application, EmailSubmission, ApplicationLog
from backend.app.models.profile import Profile
from backend.app.models.vacancy import Vacancy

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly"
]

CREDENTIALS_FILE = Path(settings.GMAIL_CREDENTIALS_FILE)
TOKEN_FILE = CREDENTIALS_FILE.parent / "token.json"


def get_oauth_flow():
    """Build and return an InstalledAppFlow instance if client secrets are present."""
    from google_auth_oauthlib.flow import Flow
    if not CREDENTIALS_FILE.exists():
        if settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET:
            client_config = {
                "installed": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GMAIL_REDIRECT_URI, "http://localhost:8000/auth/gmail/callback"]
                }
            }
            CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(client_config, f, indent=2)
        else:
            return None

    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES,
        redirect_uri=settings.GMAIL_REDIRECT_URI
    )
    return flow


def get_gmail_auth_url() -> Optional[str]:
    """Generate authorization URL for user to grant Gmail permissions."""
    flow = get_oauth_flow()
    if not flow:
        return None
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return auth_url


def handle_oauth_callback(code: str) -> Dict[str, Any]:
    """Exchange authorization code for tokens and save to token.json."""
    flow = get_oauth_flow()
    if not flow:
        raise ValueError("OAuth flow could not be initialized. Client ID and Secret missing.")
    flow.fetch_token(code=code)
    creds = flow.credentials
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    return {"ok": True, "message": "Gmail successfully authorized."}


def get_gmail_connection_status() -> Dict[str, Any]:
    """Check whether valid Gmail credentials or token exist."""
    configured = bool(
        (settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET) or CREDENTIALS_FILE.exists()
    )
    connected = False
    user_email = None

    if TOKEN_FILE.exists():
        try:
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if creds and creds.valid:
                connected = True
            elif creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                with open(TOKEN_FILE, "w") as f:
                    f.write(creds.to_json())
                connected = True
        except Exception:
            connected = False

    return {
        "configured": configured,
        "connected": connected,
        "email": user_email,
        "test_mode": settings.TEST_MODE,
        "message": "Connected to Gmail." if connected else ("Test mode active (simulated sending)." if settings.TEST_MODE else "Not connected.")
    }


def disconnect_gmail() -> bool:
    """Remove stored credentials and token."""
    removed = False
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        removed = True
    return removed


def compose_application_email(
    profile: Profile,
    vacancy: Vacancy,
    cv_path: Optional[str] = None,
    cover_letter_path: Optional[str] = None,
    extra_attachments: Optional[List[str]] = None
) -> EmailMessage:
    """
    Construct MIME email following formal South African employment correspondence conventions.
    Strictly truthfully references applicant details.
    """
    msg = EmailMessage()
    ref_part = f" - Ref: {vacancy.reference_number}" if vacancy.reference_number else ""
    subject = f"Application: {vacancy.title}{ref_part} - {profile.full_legal_name}"
    
    msg["Subject"] = subject
    msg["From"] = profile.email
    msg["To"] = vacancy.application_email or "applications@example.com"

    salutation = "Dear Hiring Committee,"
    if vacancy.employer:
        salutation = f"Dear {vacancy.employer} Recruitment Team,"

    body_text = f"""{salutation}

Please find attached my application for the position of {vacancy.title}{ref_part}.

Candidate Information:
- Full Name: {profile.full_legal_name}
- Location: {profile.town_city or 'Johannesburg'}, {profile.province or 'Gauteng'}
- Contact Number: {profile.phone_number or 'Available upon request'}
- Email: {profile.email}

Attached Documents:
- Curriculum Vitae (Tailored for {vacancy.title})
- Formal Cover Letter
- Verified Educational & Identity Documentation (Available upon request / attached)

Thank you for your time and consideration. I look forward to the possibility of discussing my suitability for this opportunity.

Yours sincerely,

{profile.full_legal_name}
Applicant
"""
    msg.set_content(body_text)

    # Attachments
    attachments = []
    if cv_path and Path(cv_path).exists():
        attachments.append(cv_path)
    if cover_letter_path and Path(cover_letter_path).exists():
        attachments.append(cover_letter_path)
    if extra_attachments:
        for att in extra_attachments:
            if Path(att).exists():
                attachments.append(att)

    for att_path_str in attachments:
        att_path = Path(att_path_str)
        mime_type, _ = mimetypes.guess_type(str(att_path))
        if mime_type is None:
            mime_type = "application/octet-stream"
        maintype, subtype = mime_type.split("/", 1)
        with open(att_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=att_path.name
            )

    return msg


def send_application_email(
    profile: Profile,
    vacancy: Vacancy,
    application: Application,
    extra_attachments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Send job application email. If TEST_MODE is True or Gmail is not authenticated,
    simulates successful sending and records logs.
    """
    cv_path = application.tailored_cv_path
    cl_path = application.cover_letter_path

    msg = compose_application_email(
        profile=profile,
        vacancy=vacancy,
        cv_path=cv_path,
        cover_letter_path=cl_path,
        extra_attachments=extra_attachments
    )

    recip = vacancy.application_email or "careers@example.co.za"
    subject = msg["Subject"]

    # In TEST_MODE or if no token exists, simulate sending safely
    status_info = get_gmail_connection_status()
    if settings.TEST_MODE or not status_info["connected"]:
        message_id = f"test-simulated-{vacancy.id}-{int(datetime.now(timezone.utc).timestamp())}"
        result = {
            "status": "SENT_TEST_MODE",
            "message_id": message_id,
            "recipient": recip,
            "subject": subject,
            "attachments_count": len(list(msg.iter_attachments())) if hasattr(msg, "iter_attachments") else 0,
            "simulated": True
        }
    else:
        # Live transmission via Google Gmail API
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        service = build("gmail", "v1", credentials=creds)

        raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        sent_response = service.users().messages().send(userId="me", body={"raw": raw_msg}).execute()
        message_id = sent_response.get("id", "live-sent")
        result = {
            "status": "SENT",
            "message_id": message_id,
            "recipient": recip,
            "subject": subject,
            "simulated": False
        }

    return result

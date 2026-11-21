from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class EmailSubmissionOut(BaseModel):
    id: int
    recipient_email: str
    subject: str
    gmail_message_id: Optional[str] = None
    attachments: Optional[str] = None
    sent_at: Optional[datetime] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class WebsiteSubmissionOut(BaseModel):
    id: int
    portal_url: str
    submission_reference: Optional[str] = None
    screenshot_path: Optional[str] = None
    submitted_at: Optional[datetime] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationOut(BaseModel):
    id: int
    vacancy_id: int
    profile_id: Optional[int] = None
    status: str
    application_method: str
    tailored_cv_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    email_submission: Optional[EmailSubmissionOut] = None
    website_submission: Optional[WebsiteSubmissionOut] = None

    model_config = ConfigDict(from_attributes=True)

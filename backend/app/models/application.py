from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, SUBMITTED, FAILED, REQUIRES_ATTENTION, PAUSED
    application_method = Column(String(50), default="email")  # email, website
    tailored_cv_path = Column(String(500), nullable=True)
    cover_letter_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    vacancy = relationship("Vacancy", back_populates="applications")
    email_submission = relationship("EmailSubmission", uselist=False, back_populates="application", cascade="all, delete-orphan")
    website_submission = relationship("WebsiteSubmission", uselist=False, back_populates="application", cascade="all, delete-orphan")
    logs = relationship("ApplicationLog", back_populates="application", cascade="all, delete-orphan")


class EmailSubmission(Base):
    __tablename__ = "email_submissions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, nullable=False)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    gmail_message_id = Column(String(255), nullable=True)
    attachments = Column(Text, nullable=True)  # JSON list of attached documents
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(50), default="SENT")  # SENT, FAILED, QUEUED

    application = relationship("Application", back_populates="email_submission")


class WebsiteSubmission(Base):
    __tablename__ = "website_submissions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, nullable=False)
    portal_url = Column(String(1000), nullable=False)
    submission_reference = Column(String(255), nullable=True)
    screenshot_path = Column(String(500), nullable=True)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(50), default="SUBMITTED")

    application = relationship("Application", back_populates="website_submission")


class ApplicationLog(Base):
    __tablename__ = "application_logs"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    level = Column(String(20), default="INFO")
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates="logs")

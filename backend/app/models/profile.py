from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    full_legal_name = Column(String(255), nullable=False)
    id_number = Column(String(255), nullable=True)  # Stored securely / masked
    phone_number = Column(String(50), nullable=True)
    email = Column(String(255), nullable=False)
    residential_address = Column(String(255), nullable=True)
    province = Column(String(100), nullable=True)
    town_city = Column(String(100), nullable=True)
    drivers_licence = Column(String(50), nullable=True)
    has_own_transport = Column(Boolean, default=False)
    languages = Column(String(255), default="English")
    is_verified = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    qualifications = relationship("Qualification", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    references = relationship("Reference", back_populates="profile", cascade="all, delete-orphan")


class Qualification(Base):
    __tablename__ = "qualifications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    qualification_name = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=True)
    field_of_study = Column(String(255), nullable=True)
    nqf_level = Column(String(50), nullable=True)
    start_year = Column(String(20), nullable=True)
    end_year = Column(String(20), nullable=True)
    is_completed = Column(Boolean, default=True)
    subjects_and_results = Column(Text, nullable=True)  # JSON formatted subjects
    is_verified = Column(Boolean, default=False)
    supporting_document_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    profile = relationship("Profile", back_populates="qualifications")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(100), default="Technical")
    proficiency = Column(String(50), default="Intermediate")
    is_verified = Column(Boolean, default=False)

    profile = relationship("Profile", back_populates="skills")


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    job_title = Column(String(255), nullable=False)
    employer = Column(String(255), nullable=False)
    location = Column(String(100), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    is_current = Column(Boolean, default=False)
    responsibilities = Column(Text, nullable=True)
    is_volunteer = Column(Boolean, default=False)

    profile = relationship("Profile", back_populates="experiences")


class Reference(Base):
    __tablename__ = "references"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    full_name = Column(String(255), nullable=False)
    relationship_type = Column(String(100), nullable=True)
    organization = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)

    profile = relationship("Profile", back_populates="references")

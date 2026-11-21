"""
BOB Job Discovery Base Adapter Architecture
Defines the contract for all South African vacancy source adapters.
Ensures uniform extraction of the 19 required vacancy fields and cryptographic fingerprinting.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import hashlib
import re
from pydantic import BaseModel, Field


class RawVacancy(BaseModel):
    """Normalized South African vacancy representation containing all mandatory attributes."""
    title: str = Field(..., description="Job title")
    employer: str = Field(..., description="Employing department, company or municipality")
    location: Optional[str] = Field(None, description="City, town, or station")
    province: Optional[str] = Field(None, description="South African Province")
    salary: Optional[str] = Field(None, description="Salary scale, package or stipend")
    employment_type: str = Field("Full-time", description="Full-time, Contract, Internship, Learnership")
    qualification_requirements: Optional[str] = Field(None, description="Required education/qualifications")
    experience_requirements: Optional[str] = Field(None, description="Required years/type of experience")
    skills_requirements: Optional[str] = Field(None, description="Required technical/soft skills")
    age_requirements: Optional[str] = Field(None, description="Youth or age limits if specified")
    drivers_licence_required: Optional[str] = Field(None, description="Licence code if required (Code B, C, EC)")
    citizenship_required: Optional[str] = Field("South African", description="Citizenship or residency criteria")
    required_documents: Optional[str] = Field(None, description="e.g. CV, Certified ID, Matric, Z83")
    application_method: str = Field("email", description="email or website")
    application_email: Optional[str] = Field(None, description="Official email address for submissions")
    application_url: Optional[str] = Field(None, description="Application link or career portal URL")
    closing_date: Optional[str] = Field(None, description="Application deadline date")
    reference_number: Optional[str] = Field(None, description="Circular or post reference number")
    description: str = Field(..., description="Complete original vacancy advertisement text")
    source_url: str = Field(..., description="Original URL where post was discovered")
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_fingerprint(self) -> str:
        """
        Generate a deterministic SHA-256 fingerprint for deduplication.
        Combines normalized title, employer, reference number, and source URL.
        """
        norm_title = re.sub(r"\s+", " ", self.title.strip().lower())
        norm_emp = re.sub(r"\s+", " ", self.employer.strip().lower())
        norm_ref = re.sub(r"\s+", "", (self.reference_number or "").strip().lower())
        norm_src = self.source_url.strip().lower()

        raw_key = f"{norm_title}|{norm_emp}|{norm_ref}|{norm_src}".encode("utf-8")
        return hashlib.sha256(raw_key).hexdigest()


class BaseSourceAdapter(ABC):
    """Abstract base class for all job vacancy source scrapers and API adapters."""

    def __init__(self, name: str, source_type: str, base_url: str):
        self.name = name
        self.source_type = source_type  # "government", "retail_corporate", "internships_learnerships"
        self.base_url = base_url
        self.user_agent = "BOB-SA-JobAgent/1.0 (+https://za.co.bob.desktop; autonomous job search)"

    @abstractmethod
    async def fetch_vacancies(self) -> List[RawVacancy]:
        """
        Fetch and parse open vacancies from the target source.
        Returns a list of validated RawVacancy objects.
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """Metadata about this adapter."""
        return {
            "name": self.name,
            "source_type": self.source_type,
            "base_url": self.base_url,
            "is_active": True
        }

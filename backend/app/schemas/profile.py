from pydantic import BaseModel, ConfigDict, computed_field
from typing import List, Optional
from datetime import datetime


class QualificationBase(BaseModel):
    qualification_name: str
    institution: Optional[str] = None
    field_of_study: Optional[str] = None
    nqf_level: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None
    is_completed: bool = True
    subjects_and_results: Optional[str] = None
    is_verified: bool = False
    supporting_document_id: Optional[int] = None


class QualificationCreate(QualificationBase):
    pass


class QualificationOut(QualificationBase):
    id: int
    profile_id: int

    @computed_field
    @property
    def name(self) -> str:
        return self.qualification_name

    @computed_field
    @property
    def year_obtained(self) -> Optional[str]:
        return self.end_year

    model_config = ConfigDict(from_attributes=True)


class SkillBase(BaseModel):
    name: str
    category: str = "Technical"
    proficiency: str = "Intermediate"
    is_verified: bool = False


class SkillCreate(SkillBase):
    pass


class SkillOut(SkillBase):
    id: int
    profile_id: int

    @computed_field
    @property
    def proficiency_level(self) -> str:
        return self.proficiency

    model_config = ConfigDict(from_attributes=True)


class ExperienceBase(BaseModel):
    job_title: str
    employer: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    responsibilities: Optional[str] = None
    is_volunteer: bool = False


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceOut(ExperienceBase):
    id: int
    profile_id: int

    @computed_field
    @property
    def description(self) -> Optional[str]:
        return self.responsibilities

    model_config = ConfigDict(from_attributes=True)


class ReferenceBase(BaseModel):
    full_name: str
    relationship_type: Optional[str] = None
    organization: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ReferenceCreate(ReferenceBase):
    pass


class ReferenceOut(ReferenceBase):
    id: int
    profile_id: int

    model_config = ConfigDict(from_attributes=True)


class ProfileBase(BaseModel):
    full_legal_name: str
    id_number: Optional[str] = None
    phone_number: Optional[str] = None
    email: str
    residential_address: Optional[str] = None
    province: Optional[str] = None
    town_city: Optional[str] = None
    drivers_licence: Optional[str] = None
    has_own_transport: bool = False
    languages: str = "English"
    is_verified: bool = False
    notes: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    full_legal_name: Optional[str] = None
    full_name: Optional[str] = None
    id_number: Optional[str] = None
    phone_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    residential_address: Optional[str] = None
    address: Optional[str] = None
    province: Optional[str] = None
    town_city: Optional[str] = None
    city: Optional[str] = None
    drivers_licence: Optional[str] = None
    has_own_transport: Optional[bool] = None
    languages: Optional[str] = None
    is_verified: Optional[bool] = None
    notes: Optional[str] = None


class ProfileOut(ProfileBase):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    qualifications: List[QualificationOut] = []
    skills: List[SkillOut] = []
    experiences: List[ExperienceOut] = []
    references: List[ReferenceOut] = []

    @computed_field
    @property
    def full_name(self) -> str:
        return self.full_legal_name

    @computed_field
    @property
    def phone(self) -> Optional[str]:
        return self.phone_number

    @computed_field
    @property
    def city(self) -> Optional[str]:
        return self.town_city

    @computed_field
    @property
    def address(self) -> Optional[str]:
        return self.residential_address

    model_config = ConfigDict(from_attributes=True)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.profile import Profile, Qualification, Skill, Experience, Reference
from backend.app.schemas.profile import (
    ProfileOut, ProfileUpdate,
    QualificationCreate, QualificationOut,
    SkillCreate, SkillOut,
    ExperienceCreate, ExperienceOut,
    ReferenceCreate, ReferenceOut
)

router = APIRouter(prefix="/profile", tags=["Profile"])


def get_or_create_initial_profile(db: Session) -> Profile:
    profile = db.query(Profile).first()
    if not profile:
        # Initial South African profile based on user specifications:
        # - Matric completed
        # - Marketing Management N5 certificate supplied
        # - No formal employment experience reported
        # - South African job market
        profile = Profile(
            full_legal_name="Candidate Name",
            id_number="Pending Document Verification",
            phone_number="",
            email="candidate@example.co.za",
            residential_address="",
            province="Gauteng",
            town_city="Johannesburg",
            drivers_licence="None",
            has_own_transport=False,
            languages="English, isiZulu",
            is_verified=False,
            notes="Initial profile initialized with verified education facts: Matric and Marketing Management N5."
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        # Add initial qualifications
        matric = Qualification(
            profile_id=profile.id,
            qualification_name="National Senior Certificate (Matric)",
            institution="Department of Basic Education",
            field_of_study="General Secondary Education",
            nqf_level="NQF Level 4",
            is_completed=True,
            is_verified=True,
            subjects_and_results="Matric subjects passed"
        )
        n5_cert = Qualification(
            profile_id=profile.id,
            qualification_name="Marketing Management N5",
            institution="South African TVET College",
            field_of_study="Marketing Management",
            nqf_level="NQF Level 5",
            is_completed=True,
            is_verified=True,
            subjects_and_results="Marketing Communication, Management Communication, Marketing Management"
        )
        db.add_all([matric, n5_cert])

        # Add initial verifiable skills
        skills = [
            Skill(profile_id=profile.id, name="Marketing Fundamentals", category="Marketing", proficiency="Intermediate", is_verified=True),
            Skill(profile_id=profile.id, name="Computer Literacy (MS Office)", category="Technical", proficiency="Intermediate", is_verified=False),
            Skill(profile_id=profile.id, name="Customer Relations", category="Interpersonal", proficiency="Intermediate", is_verified=False),
            Skill(profile_id=profile.id, name="Administrative Support", category="Administrative", proficiency="Beginner", is_verified=False)
        ]
        db.add_all(skills)

        db.commit()
        db.refresh(profile)

    return profile


@router.get("", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db)):
    """Fetch the active user employment profile."""
    return get_or_create_initial_profile(db)


@router.put("", response_model=ProfileOut)
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db)):
    """Update profile information."""
    profile = get_or_create_initial_profile(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/qualifications", response_model=QualificationOut)
def add_qualification(data: QualificationCreate, db: Session = Depends(get_db)):
    profile = get_or_create_initial_profile(db)
    qual = Qualification(**data.model_dump(), profile_id=profile.id)
    db.add(qual)
    db.commit()
    db.refresh(qual)
    return qual


@router.delete("/qualifications/{qual_id}")
def delete_qualification(qual_id: int, db: Session = Depends(get_db)):
    qual = db.query(Qualification).filter(Qualification.id == qual_id).first()
    if not qual:
        raise HTTPException(status_code=404, detail="Qualification not found")
    db.delete(qual)
    db.commit()
    return {"message": "Qualification deleted successfully"}


@router.post("/skills", response_model=SkillOut)
def add_skill(data: SkillCreate, db: Session = Depends(get_db)):
    profile = get_or_create_initial_profile(db)
    skill = Skill(**data.model_dump(), profile_id=profile.id)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return {"message": "Skill deleted successfully"}


@router.post("/experiences", response_model=ExperienceOut)
def add_experience(data: ExperienceCreate, db: Session = Depends(get_db)):
    profile = get_or_create_initial_profile(db)
    exp = Experience(**data.model_dump(), profile_id=profile.id)
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/experiences/{exp_id}")
def delete_experience(exp_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    db.delete(exp)
    db.commit()
    return {"message": "Experience deleted successfully"}


@router.post("/references", response_model=ReferenceOut)
def add_reference(data: ReferenceCreate, db: Session = Depends(get_db)):
    profile = get_or_create_initial_profile(db)
    ref = Reference(**data.model_dump(), profile_id=profile.id)
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ref


@router.delete("/references/{ref_id}")
def delete_reference(ref_id: int, db: Session = Depends(get_db)):
    ref = db.query(Reference).filter(Reference.id == ref_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found")
    db.delete(ref)
    db.commit()
    return {"message": "Reference deleted successfully"}

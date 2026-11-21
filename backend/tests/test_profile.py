import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_get_initial_profile():
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()

    assert data["email"] is not None
    assert len(data["qualifications"]) >= 2

    # Check verified Matric and N5 qualifications
    qual_names = [q["qualification_name"] for q in data["qualifications"]]
    assert any("Matric" in name for name in qual_names)
    assert any("Marketing Management N5" in name for name in qual_names)

    # Check initial skills
    skill_names = [s["name"] for s in data["skills"]]
    assert "Marketing Fundamentals" in skill_names


def test_update_profile():
    update_data = {
        "full_legal_name": "Verified Candidate Name",
        "phone_number": "+27 82 123 4567",
        "town_city": "Pretoria",
        "province": "Gauteng",
        "drivers_licence": "Code B (08)"
    }
    response = client.put("/api/profile", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_legal_name"] == "Verified Candidate Name"
    assert data["phone_number"] == "+27 82 123 4567"
    assert data["town_city"] == "Pretoria"
    assert data["drivers_licence"] == "Code B (08)"


def test_add_and_delete_skill():
    # Add skill
    new_skill = {
        "name": "Social Media Marketing",
        "category": "Marketing",
        "proficiency": "Advanced",
        "is_verified": True
    }
    create_res = client.post("/api/profile/skills", json=new_skill)
    assert create_res.status_code == 200
    skill_data = create_res.json()
    assert skill_data["name"] == "Social Media Marketing"
    skill_id = skill_data["id"]

    # Delete skill
    delete_res = client.delete(f"/api/profile/skills/{skill_id}")
    assert delete_res.status_code == 200
    assert "deleted successfully" in delete_res.json()["message"]

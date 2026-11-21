import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_list_vacancies():
    response = client.get("/api/vacancies")
    assert response.status_code == 200
    vacancies = response.json()
    assert len(vacancies) >= 1
    # Check that first vacancy has eligibility evaluation
    v1 = vacancies[0]
    assert "title" in v1
    assert "employer" in v1
    assert "eligibility_decision" in v1


def test_stats_and_settings():
    stats_res = client.get("/api/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_discovered" in stats
    assert "eligible_count" in stats
    assert "agent_status" in stats

    settings_res = client.get("/api/settings")
    assert settings_res.status_code == 200
    cfg = settings_res.json()
    assert cfg["app_name"] == "Bob"
    assert cfg["job_market"] == "South Africa"


def test_toggle_pause():
    # Toggle pause
    res1 = client.post("/api/settings/toggle-pause")
    assert res1.status_code == 200
    state1 = res1.json()["is_paused"]

    # Toggle back
    res2 = client.post("/api/settings/toggle-pause")
    assert res2.status_code == 200
    state2 = res2.json()["is_paused"]
    assert state1 != state2

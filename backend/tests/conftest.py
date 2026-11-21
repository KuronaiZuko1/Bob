import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.api.profile import get_or_create_initial_profile
from backend.app.main import seed_sample_data


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        get_or_create_initial_profile(db)
        seed_sample_data(db)
    finally:
        db.close()
    yield

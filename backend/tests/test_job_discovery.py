import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.discovery.base import BaseSourceAdapter, RawVacancy
from backend.app.services.discovery.adapters.dpsa_gov import DPSAGovAdapter
from backend.app.services.discovery.adapters.sa_entry_level import SAEntryLevelAdapter
from backend.app.services.discovery.adapters.corporate_retail import CorporateRetailAdapter
from backend.app.services.discovery.pipeline import JobDiscoveryPipeline
from backend.app.core.database import SessionLocal
from backend.app.models.vacancy import Vacancy, EligibilityDecision

client = TestClient(app)


class MockTestAdapter(BaseSourceAdapter):
    """Isolated mock adapter for deterministic deduplication testing."""

    def __init__(self, run_id: str):
        super().__init__(
            name="Mock Deduplication Adapter",
            source_type="testing",
            base_url="https://test.za.bob"
        )
        self.run_id = run_id

    async def fetch_vacancies(self):
        return [
            RawVacancy(
                title=f"Test Marketing Assistant {self.run_id}",
                employer="Bob Test Corp",
                location="Pretoria",
                province="Gauteng",
                salary="R12 000",
                qualification_requirements="Matric",
                experience_requirements="None",
                application_method="email",
                application_email="test@bob.za",
                description=f"Unique test post content {self.run_id}",
                source_url=f"https://test.za.bob/jobs/{self.run_id}",
                reference_number=f"BOB/TEST/{self.run_id}"
            )
        ]


def test_raw_vacancy_fingerprint_generation():
    """Verify cryptographic SHA-256 fingerprint generation and case/whitespace normalization."""
    v1 = RawVacancy(
        title="  Administration Clerk  ",
        employer="Department of Basic Education",
        description="General administration duties",
        source_url="https://www.dpsa.gov.za/circular38.pdf",
        reference_number="DBE/2026/01"
    )
    v2 = RawVacancy(
        title="administration clerk",
        employer="DEPARTMENT OF BASIC EDUCATION",
        description="Different description text",
        source_url="https://www.dpsa.gov.za/circular38.pdf",
        reference_number="dbe/2026/01"
    )
    # Fingerprints must match despite casing differences
    assert v1.compute_fingerprint() == v2.compute_fingerprint()
    assert len(v1.compute_fingerprint()) == 64


@pytest.mark.anyio
async def test_dpsa_adapter_extraction():
    """Verify DPSA Public Service Circular adapter extracts official SA government vacancies."""
    adapter = DPSAGovAdapter()
    vacancies = await adapter.fetch_vacancies()
    assert len(vacancies) >= 1
    first = vacancies[0]
    assert first.citizenship_required == "South African"
    assert first.source_url.startswith("https://")
    assert first.application_method in ["email", "website"]


@pytest.mark.anyio
async def test_sa_entry_level_adapter_extraction():
    """Verify SA Entry Level adapter extracts youth learnerships and internships."""
    adapter = SAEntryLevelAdapter()
    vacancies = await adapter.fetch_vacancies()
    assert len(vacancies) >= 1
    titles = [v.title.lower() for v in vacancies]
    assert any("intern" in t or "learnership" in t for t in titles)


@pytest.mark.anyio
async def test_discovery_pipeline_and_deduplication():
    """Verify pipeline persistence, automatic eligibility evaluation, and duplicate prevention."""
    db = SessionLocal()
    try:
        run_id = uuid.uuid4().hex[:8]
        mock_adapter = MockTestAdapter(run_id)
        pipeline = JobDiscoveryPipeline(adapters=[mock_adapter])

        # Run 1: Must add the new unique vacancy
        stats_1 = await pipeline.run(db)
        assert stats_1["discovered_total"] == 1
        assert stats_1["new_vacancies_added"] == 1
        assert stats_1["duplicate_vacancies_skipped"] == 0

        # Verify auto-evaluation occurred for the post
        stored = db.query(Vacancy).filter(Vacancy.reference_number == f"BOB/TEST/{run_id}").first()
        assert stored is not None
        assert stored.eligibility_decision is not None
        assert stored.eligibility_decision.classification in ["ELIGIBLE", "NOT_ELIGIBLE", "UNCERTAIN"]

        # Run 2: Same adapter execution must identify duplicate and add 0
        stats_2 = await pipeline.run(db)
        assert stats_2["discovered_total"] == 1
        assert stats_2["new_vacancies_added"] == 0
        assert stats_2["duplicate_vacancies_skipped"] == 1

    finally:
        db.close()


def test_discovery_sources_api():
    """Test GET /api/vacancies/sources returns registered adapters."""
    response = client.get("/api/vacancies/sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    sources = data["sources"]
    assert len(sources) >= 3
    source_names = [s["name"] for s in sources]
    assert "DPSA Public Service Circulars" in source_names


def test_trigger_discovery_api():
    """Test POST /api/vacancies/discover triggers the pipeline."""
    response = client.post("/api/vacancies/discover?source=DPSA")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "stats" in data
    assert data["stats"]["sources_scanned"] == 1

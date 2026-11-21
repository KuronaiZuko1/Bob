# Changelog

All notable changes to the BOB autonomous agent project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Phase 4: Job Discovery Engine & South African Adapters] - 2026-11-19

### Added
- **Modular Source Adapter Architecture** (`backend/app/services/discovery/base.py`):
  - `RawVacancy` Pydantic model capturing all 19 standardized South African vacancy attributes (title, employer, location, province, salary, qualification requirements, experience requirements, licence requirements, citizenship, documents, application method, contact details, closing date, reference number, description, source URL).
  - SHA-256 cryptographic vacancy fingerprinting with whitespace and case normalization.
  - `BaseSourceAdapter` abstract base class with custom User-Agent and compliant network retrieval.
- **Specialized South African Adapters** (`backend/app/services/discovery/adapters/`):
  - `DPSAGovAdapter`: Department of Public Service and Administration official Public Service Circulars (Level 5 administration clerks, registry clerks, communication officers, Z83 applications).
  - `SAEntryLevelAdapter`: South African youth learnerships (SETA-accredited), internships (Vodacom, Massmart), and entry-level positions.
  - `CorporateRetailAdapter`: Major South African commercial and retail career portals (Shoprite, Capitec, Sasol).
- **Discovery Pipeline Coordinator** (`backend/app/services/discovery/pipeline.py`):
  - 3-point deduplication across SHA-256 fingerprints, source URLs, and reference numbers.
  - Automatic seamless invocation of the Phase 3 AI Eligibility Engine on all newly discovered posts.
  - Automatic audit logging and `SearchHistory` recording.
- **REST Endpoints & Frontend UI**:
  - `GET /api/vacancies/sources`: Lists available source adapters and metadata.
  - `POST /api/vacancies/discover`: Triggers live discovery with optional source filtering.
  - Integrated "Scan Sources Now" action in `frontend/src/pages/Discovery.jsx` with real-time feedback.
- **Automated Test Suite**:
  - Added `backend/tests/test_job_discovery.py` covering fingerprint normalization, adapter extraction, pipeline deduplication, and API triggers.
  - **24/24 tests passing** across the complete backend test suite.

---

## [Phase 3: AI Engine & Structured Eligibility Decisions] - 2026-11-18

### Added
- **Multi-Tier AI Eligibility Engine** (`backend/app/services/ai_provider.py`):
  - Local Ollama inference integration using structured JSON output.
  - OpenAI-compatible API integration (`gpt-4o-mini` or custom endpoints).
  - High-precision deterministic fallback engine ensuring zero downtime when local LLM is offline.
  - Anti-prompt injection filters safeguarding against untrusted vacancy contents.
  - Strict 3-state classification: `ELIGIBLE`, `NOT_ELIGIBLE`, and `UNCERTAIN`.
  - Zero-invention guardrails: only verified qualifications, experience, and licences from the user profile are compared.
- **REST Endpoints & Schema Extensions**:
  - `POST /api/vacancies/{id}/evaluate`: Runs AI/deterministic evaluation against the current profile and persists structured decision.
  - `POST /api/settings/test-ai`: Diagnoses AI connection and confirms fallback availability.
  - Computed fields on `VacancyOut` for `eligibility_status` and `eligibility_explanation`.
- **Automated Test Suite**:
  - Added `backend/tests/test_ai_eligibility.py` covering prompt sanitization, internship eligibility matching, senior role rejection, licence uncertainty detection, and live evaluation endpoints.

---

## [Phase 2: User Profile & Secure Document Vault] - 2026-11-18

### Added
- **Fernet Authenticated Encryption Vault** (`backend/app/services/vault.py`):
  - AES-128-CBC and HMAC-SHA256 authenticated encryption at rest using Fernet.
  - SHA-256 cryptographic checksum calculation for file integrity.
  - Zero-overwrite data sanitization before unlinking deleted files.
- **Document Processing Engine** (`backend/app/services/document_processor.py`):
  - PDF text extraction via `pypdf`.
  - DOCX text and table parsing via `python-docx`.
  - Image inspection and format verification via `Pillow`.
  - Automatic South African document classification detecting ID documents, Matric certificates, College/TVET/N5 certificates, transcripts, CVs, cover letters, and utility bills.
  - SA 13-digit ID number privacy masking utility.
- **REST API Endpoints** (`backend/app/api/documents.py`):
  - `POST /api/documents/upload`: Multipart upload with automated text extraction, classification, and encryption at rest.
  - `GET /api/documents`: List stored documents with safe metadata.
  - `GET /api/documents/{id}/preview`: On-the-fly streaming decryption for viewing/downloading original documents.
  - `POST /api/documents/{id}/verify`: Verification status management.
  - `DELETE /api/documents/{id}`: Secure disk wipe and database record deletion.

---

## [Phase 1: Foundation & Desktop Application] - 2026-11-18

### Added
- Configured project environment with Python 3.15.2 venv and Node.js v20.18.0 LTS.
- Added environment configuration (`.env` and `.env.example`) and security gitignore rules (`.gitignore`).
- Established build progress, known issues, and changelog tracking files.
- FastAPI backend foundation with modular routers: `/api/health`, `/api/profile`, `/api/vacancies`, `/api/applications`, `/api/documents`, `/api/settings`, `/api/stats`.
- SQLAlchemy models and SQLite database initialization (`bob.db`) with Alembic migration scaffolding.
- Pydantic v2 schemas across all data entities using `ConfigDict(from_attributes=True)`.
- Initial seed data loading: verified Matric and Marketing Management N5 qualification profile, plus 3 sample South African vacancies (Marketing Intern, Senior Brand Manager, Admin Clerk) with structured eligibility evaluations.
- Pytest automated test suite with 8 unit and integration tests passing.
- React 18 + Vite desktop dashboard frontend with dark navy (`#0d1117`, `#161b22`) theme and blue accents.
- Complete navigation architecture with 9 functional views: Overview, Profile, Discovery, Applications, Documents, AI Config, Email, Telegram, Settings.
- Electron 29 desktop shell configuration (`electron/main.js`, `electron/preload.js`) with isolated IPC bridge and child process backend spawning.
- Vite production build verification (`dist/` generated with 0 errors).
- Electron binary download, installation, and executable path verification.

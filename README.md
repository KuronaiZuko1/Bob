# BOB — Autonomous AI Job Application Agent 🇿🇦

BOB is a privacy-first, autonomous South African desktop AI job-hunting and application agent. BOB searches official employment portals, reads vacancies, matches requirements against verified candidate credentials, tailors truthful CVs and cover letters, applies via email or website, and keeps you updated in real-time via desktop dashboard and Telegram.

---

## 🚀 Key Features

1. **Official South African Discovery Engine**: Scans DPSA (Department of Public Service and Administration), provincial careers portals, corporate entry-level, youth learnerships, and retail job boards with automated 3-point deduplication.
2. **Deterministic & Local AI Eligibility Engine**: 3-tier classification (`ELIGIBLE`, `NOT_ELIGIBLE`, `UNCERTAIN`). BOB **never fabricates credentials, experience, references, or skills**.
3. **Tailored Truthful Document Generation**: Generates ATS-optimized CVs (PDF & DOCX via ReportLab & python-docx) and formal SA cover letters tailored directly to job titles and reference numbers.
4. **Automated Submission**:
   - **Gmail API**: OAuth 2.0 integration for official direct email submissions.
   - **Playwright Website Automation**: Automated portal submission with pre-submit verification and full-page screenshot evidence.
5. **Encrypted Document Vault**: AES-128 Fernet encrypted storage with automatic SA ID number masking.
6. **Telegram Bot Control**: Command and monitor BOB anywhere (`/status`, `/stats`, `/pause`, `/resume`, `/vacancies`, `/applied`).
7. **Autonomous Background Scheduler**: Runs periodic discovery, evaluation, and application dispatching automatically.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Alembic, SQLite
- **Frontend / Desktop Shell**: Electron 29, React 18, Vite, Lucide Icons, Vanilla CSS
- **AI Engine**: Local Ollama (e.g. Llama 3.2), OpenAI-compatible API, and built-in deterministic rule engine
- **Automation**: Playwright, APScheduler, Google Gmail API, Telegram Bot API
- **Document Processing**: ReportLab, python-docx, pypdf, Pillow, Cryptography

---

## 📦 How to Run BOB

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Git

### 1. Setup Backend
```bash
# Clone the repository
git clone https://github.com/KuronaiZuko1/Bob.git
cd Bob

# Activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# (Optional) Install Playwright browser binaries
playwright install chromium
```

### 2. Configure Environment
Copy `.env.example` to `.env` and adjust your preferences:
```ini
TEST_MODE=True            # Keeps submissions simulated safely until you are ready
AI_PROVIDER=ollama         # Or 'openai' or 'deterministic'
JOB_SEARCH_INTERVAL_HOURS=6
AUTO_APPLY_ENABLED=False   # Toggle True when ready for fully hands-free applying
```

### 3. Start Backend Server
```bash
python backend/run.py
```
Backend API docs available at: `http://localhost:8000/docs`

### 4. Setup & Launch Desktop App (Frontend)
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

To run the complete Electron desktop app:
```bash
npm run electron
```

---

## 🧪 Running Automated Tests
```bash
python -m pytest backend/tests -v
```

---

## 🔒 Security & Privacy Commitments
- **Zero Hallucination Rule**: BOB will never claim work experience, degrees, or licenses you do not have.
- **Data Privacy**: Documents are encrypted at rest using AES-128 Fernet encryption.
- **Safety Mode**: Default `TEST_MODE=True` ensures no real emails or website forms are submitted without explicit user consent.

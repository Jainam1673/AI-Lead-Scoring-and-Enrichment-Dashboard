# Backend - AI Lead Scoring & Enrichment Dashboard

FastAPI backend for automated lead enrichment and AI-powered scoring.

## 🎯 Overview

This backend service provides:
- **CSV Upload Processing**: Parse and validate lead data
- **Data Enrichment**: Add company size, industry, LinkedIn URLs, email validation
- **AI Scoring**: Rule-based scoring system (0-100 scale)
- **Export Functionality**: Download enriched leads as CSV
- **Real Dataset**: 200 realistic B2B leads from major tech, finance, healthcare, and e-commerce companies

### Sample Dataset
The `sample-leads.csv` file contains **200 realistic B2B leads** including:
- **Companies**: Google, Microsoft, Amazon, Stripe, Goldman Sachs, Netflix, Coinbase, and 70+ more
- **Industries**: Tech (60%), Finance (20%), Healthcare (10%), E-commerce (10%)
- **Job Titles**: CEO, CTO, CFO, VP, Director, Manager, and IC roles
- **Company Sizes**: 50-200 (startups), 200-1000, 1000-5000, 5000+ (enterprise)
- **Locations**: San Francisco, New York, Seattle, Boston, Austin, and 20+ other cities

## 🏗️ Architecture

```
backend/
├── src/
│   ├── app.py                    # FastAPI application setup
│   ├── models/
│   │   └── lead.py              # Pydantic models (Lead, ScoredLead)
│   ├── routes/
│   │   └── api.py               # API endpoints
│   └── utils/
│       ├── enrichment.py        # Data enrichment logic
│       └── scoring.py           # Scoring algorithm
├── main.py                      # Entry point
├── sample-leads.csv             # Demo CSV data
└── pyproject.toml               # UV dependencies
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12+
- UV package manager ([install here](https://github.com/astral-sh/uv))

### Install Dependencies
```bash
cd backend
uv sync
```

This installs:
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pandas` - CSV processing
- `python-multipart` - File upload support

### Run the Server
```bash
uv run python main.py
```

Server starts on: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

## 📡 API Endpoints

### `POST /api/upload-leads`
Upload and process CSV file with leads.

**Request:**
- Content-Type: `multipart/form-data`
- Body: CSV file with columns: `name`, `email`, `company`, `job_title`, `location` (optional), `industry` (optional)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Sarah Johnson",
    "email": "sarah@techventures.com",
    "company": "TechVentures",
    "job_title": "CEO",
    "industry": "finance",
    "location": "San Francisco CA",
    "company_size": "50-200",
    "linkedin_url": "https://linkedin.com/in/sarah-johnson",
    "email_valid": true,
    "score": 91.11,
    "score_breakdown": {
      "total_score": 91.11,
      "job_title_score": 10,
      "job_title_reason": "Job title 'CEO' matches 'ceo' pattern",
      "company_size_score": 5,
      "company_size_reason": "Company size: 50-200",
      "industry_score": 10,
      "industry_reason": "Target industry: finance",
      "email_score": 5,
      "email_reason": "Email validated successfully",
      "raw_total": 30
    },
    "enriched": true
  }
]
```

### `GET /api/leads`
Get all scored leads (returns sample data if no leads uploaded).

**Response:** Array of scored lead objects

### `GET /api/export`
Download enriched leads as CSV file.

**Response:** CSV file download

### `DELETE /api/leads`
Clear all leads from memory storage.

**Response:**
```json
{
  "message": "All leads cleared"
}
```

## 🧮 Scoring Algorithm

### Rule-Based Scoring System

The scoring algorithm evaluates leads on 4 key criteria:

#### 1. Job Title Score (0-10 points)
Decision-making authority indicator:
- CEO/Founder/Chief: 10 points
- President: 9 points
- VP/Director: 7 points
- Head: 6 points
- Manager: 5 points
- Lead: 4 points
- Senior/Engineer/Developer: 3 points
- Analyst/Coordinator: 2 points
- Intern/Assistant: 1 point

#### 2. Company Size Score (0-10 points)
Budget and deal size indicator:
- 1000+ employees: 10 points
- 200-1000 employees: 7 points
- 50-200 employees: 5 points
- 10-50 employees: 3 points

#### 3. Industry Match Score (0-10 points)
Alignment with target market:
- Target industries (tech, finance, healthcare): 10 points
- Related industries (consulting, ecommerce, media): 5 points
- Other industries: 0 points

#### 4. Email Validation (-10 to +5 points)
Data quality indicator:
- Valid email: +5 points
- Invalid email: -10 points (heavy penalty)
- Unknown: 0 points

### Score Normalization

```python
raw_score = job_title + company_size + industry + email_validation
# Raw range: -10 to 35
normalized_score = ((raw_score + 10) / 45) * 100
# Final range: 0 to 100
```

### Score Interpretation
- **70-100**: High-priority lead (green badge)
- **40-69**: Medium-priority lead (yellow badge)
- **0-39**: Low-priority lead (red badge)

## 🔍 Data Enrichment

### Company Size Classification
Uses pattern matching and mock database:
- Known companies → lookup table
- Unknown → heuristics based on company name patterns

### Industry Classification  
Matches company name against industry patterns:
- "tech", "software", "saas" → tech
- "capital", "bank", "invest" → finance
- "health", "medical", "pharma" → healthcare
- etc.

### LinkedIn URL Generation
Creates likely profile URL from name:
```python
"John Smith" → "https://linkedin.com/in/john-smith"
```

### Email Validation
- Regex pattern matching
- Domain blacklist checking (test.com, fake.com, etc.)

**Note:** In production, these would call external APIs like Clearbit, Hunter.io, or RocketReach.

## 🧪 Testing

Install optional test dependencies (httpx) if you plan to run API smoke tests via TestClient:

```bash
uv --directory backend sync --extra dev
```

### Manual Testing with cURL

```bash
# Upload leads
curl -X POST http://localhost:8000/api/upload-leads \
  -F "file=@sample-leads.csv"

# Get leads
curl http://localhost:8000/api/leads

# Export leads
curl http://localhost:8000/api/export -o enriched_leads.csv
```

### Using the Interactive Docs

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.

## 🔧 Configuration

### CORS Settings
Currently allows frontend on `http://localhost:3000`. Update in `src/app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Scoring Weights
Customize scoring in `src/utils/scoring.py`:
- Modify `JOB_TITLE_SCORES` dictionary
- Update `TARGET_INDUSTRIES` list
- Adjust `EMAIL_VALID_BONUS` and `EMAIL_INVALID_PENALTY`

## 📦 Dependencies

Managed via UV package manager:

```toml
[project]
dependencies = [
    "fastapi>=0.118.0",      # Web framework
    "uvicorn>=0.37.0",       # ASGI server
    "pydantic>=2.12.0",      # Data validation
    "pandas>=2.3.3",         # Data processing
    "python-multipart>=0.0.20", # File uploads
]
```

## 🚀 Production Deployment

### Using UV
```bash
uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker (add Dockerfile)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
CMD ["uv", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0"]
```

### Environment Variables
```bash
export PORT=8000
export CORS_ORIGINS="https://yourdomain.com"
export DATABASE_URL="postgresql://..."  # Future database
```

## 🛠️ Future Enhancements

- [ ] PostgreSQL database integration
- [ ] Real API integrations (Clearbit, Hunter.io)
- [ ] User authentication & API keys
- [ ] Rate limiting
- [ ] Caching layer (Redis)
- [ ] Background job processing (Celery)
- [ ] ML model training pipeline
- [ ] WebSocket for real-time updates

## 📝 License

MIT License

---

**Part of AI Lead Scoring & Enrichment Dashboard**
Built for Caprae Capital Full Stack Developer Challenge

This is the Python backend using FastAPI, managed with uv.

## Setup

1. Ensure uv is installed.
2. Install dependencies: `uv sync`
3. Run the server: `uv run main.py`

## API Endpoints

- `GET /api/leads`: Get mock scored leads
- `POST /api/upload-leads`: Upload CSV file to score leads

## Features

- Rule-based, explainable lead scoring (0–100)
- Automated data enrichment (company size, industry, LinkedIn URL, email validation)
- CSV upload, storage, and export pipeline
- CORS configured for the Next.js frontend
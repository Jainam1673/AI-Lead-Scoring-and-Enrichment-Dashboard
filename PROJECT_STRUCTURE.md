# Project Structure

## Overview

AI Lead Scoring and Enrichment Dashboard - A full-stack application with ML pipeline for B2B lead management.

```
AI-Lead-Scoring-and-Enrichment-Dashboard/
├── README.md                           # Main project documentation
├── ML_PIPELINE.md                      # Comprehensive ML pipeline documentation
├── DEPLOYMENT.md                       # Deployment and setup guide
├── .gitignore                          # Git ignore rules
│
├── backend/                            # FastAPI Backend
│   ├── main.py                         # Application entry point
│   ├── pyproject.toml                  # Python dependencies (uv)
│   ├── uv.lock                         # Dependency lock file
│   ├── .python-version                 # Python version specification
│   ├── .gitignore                      # Backend-specific ignores
│   ├── .env.example                    # Environment variables template
│   ├── README.md                       # Backend-specific documentation
│   ├── DATASET.md                      # Dataset documentation
│   │
│   ├── src/                            # Source code
│   │   ├── app.py                      # FastAPI application setup
│   │   │
│   │   ├── models/                     # Pydantic models
│   │   │   └── lead.py                 # Lead and ScoredLead models
│   │   │
│   │   ├── routes/                     # API endpoints
│   │   │   └── api.py                  # Main API routes with ML pipeline
│   │   │
│   │   └── utils/                      # Utility modules
│   │       ├── scoring.py              # Lead scoring algorithm
│   │       ├── enrichment.py           # Data enrichment logic
│   │       ├── validation.py           # Data validation (NEW)
│   │       ├── cleaning.py             # Data cleaning (NEW)
│   │       └── pipeline.py             # ML pipeline orchestration (NEW)
│   │
│   ├── sample-leads.csv                # Sample dataset (200 leads)
│   ├── kaggle_leads.csv                # Real LinkedIn data (889 leads)
│   ├── leads_10k.csv                   # Performance test dataset (10K leads)
│   └── process_kaggle_dataset.py       # Dataset processing script
│
├── frontend/                           # Next.js Frontend
│   ├── package.json                    # Node dependencies (bun)
│   ├── bun.lock                        # Dependency lock file
│   ├── next.config.ts                  # Next.js configuration
│   ├── tsconfig.json                   # TypeScript configuration
│   ├── components.json                 # shadcn/ui configuration
│   ├── eslint.config.mjs               # ESLint configuration
│   ├── postcss.config.mjs              # PostCSS configuration
│   ├── README.md                       # Frontend-specific documentation
│   │
│   ├── public/                         # Static assets
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── ...
│   │
│   └── src/                            # Source code
│       ├── app/                        # Next.js App Router
│       │   ├── page.tsx                # Main dashboard page
│       │   ├── layout.tsx              # Root layout
│       │   ├── globals.css             # Global styles
│       │   └── favicon.ico             # Favicon
│       │
│       ├── components/                 # React components
│       │   ├── LeadTable.tsx           # Sortable leads table
│       │   ├── FiltersPanel.tsx        # Filter controls
│       │   ├── ScoreBadge.tsx          # Score visualization
│       │   ├── ProcessingProgress.tsx  # ML pipeline progress UI (NEW)
│       │   └── ui/                     # shadcn/ui components
│       │       ├── button.tsx
│       │       ├── card.tsx
│       │       ├── input.tsx
│       │       └── table.tsx
│       │
│       └── lib/                        # Utilities
│           └── utils.ts                # Utility functions
│
└── kaggle-datasets/                    # Real LinkedIn datasets (not committed)
    ├── LinkedIn people profiles datasets.csv      # 1,000 profiles
    └── LinkedIn company information datasets.csv  # 1,431 companies
```

## Module Descriptions

### Backend Modules

#### Core Application
- **`main.py`**: Entry point, starts FastAPI server with uvicorn
- **`src/app.py`**: FastAPI application initialization, CORS, middleware

#### Models (`src/models/`)
- **`lead.py`**: Pydantic models for data validation
  - `Lead`: Base lead model (name, email, company, job_title, etc.)
  - `ScoredLead`: Extends Lead with score, score_breakdown, enrichment fields

#### Routes (`src/routes/`)
- **`api.py`**: REST API endpoints
  - `POST /api/upload-leads`: Upload CSV and process through ML pipeline
  - `GET /api/leads`: Get all leads (with pagination)
  - `GET /api/export`: Export leads to CSV
  - `GET /api/processing-progress`: Real-time pipeline progress (NEW)
  - `DELETE /api/leads`: Clear all leads

#### Utilities (`src/utils/`)
- **`validation.py`**: Data validation layer (NEW)
  - Email format validation (RFC 5322)
  - Required field checking
  - Duplicate detection
  - Data quality assessment
  - Field length validation

- **`cleaning.py`**: Data cleaning and normalization (NEW)
  - Text normalization (whitespace, punctuation)
  - Name cleaning (remove titles, capitalization)
  - Email cleaning (lowercase, typo fixes)
  - Company standardization (suffix normalization)
  - Job title mapping (CEO, CTO, VP abbreviations)
  - Location parsing (state/country standardization)
  - Industry standardization
  - Duplicate removal

- **`pipeline.py`**: ML pipeline orchestration (NEW)
  - 6-stage processing pipeline
  - Progress tracking
  - Error handling and recovery
  - Quality metrics generation
  - Stage result aggregation

- **`enrichment.py`**: Data enrichment
  - Company size classification (database lookup)
  - Industry categorization
  - LinkedIn URL generation
  - Email validation

- **`scoring.py`**: Lead scoring algorithm
  - Rule-based ML scoring (0-100 scale)
  - Job title scoring (0-10 points)
  - Company size scoring (0-10 points)
  - Industry match scoring (0-10 points)
  - Email validation scoring (-10 to +5 points)
  - Score normalization

### Frontend Components

#### Pages (`src/app/`)
- **`page.tsx`**: Main dashboard page
  - File upload UI
  - Lead table display
  - Filter panel
  - Export functionality
  - Real-time stats

#### Components (`src/components/`)
- **`LeadTable.tsx`**: Interactive table with sorting
- **`FiltersPanel.tsx`**: Search and filter controls
- **`ScoreBadge.tsx`**: Visual score representation
- **`ProcessingProgress.tsx`**: ML pipeline progress UI (NEW)
  - Real-time progress bar
  - Stage-by-stage visualization
  - Success/failure indicators
  - Statistics dashboard
  - Warning/error display

#### UI Components (`src/components/ui/`)
- shadcn/ui components: button, card, input, table
- Consistent, accessible design system

## Data Files

### Datasets
- **`sample-leads.csv`**: 200 pre-scored B2B leads from major companies
- **`kaggle_leads.csv`**: 889 real LinkedIn professionals (processed)
- **`leads_10k.csv`**: 10,000 leads for performance testing

### Scripts
- **`process_kaggle_dataset.py`**: Transform raw LinkedIn data to lead format
  - Email generation from names
  - Industry mapping
  - Location extraction
  - JSON parsing (experience, company)
  - Error handling

## Configuration Files

### Backend
- **`pyproject.toml`**: Python dependencies, project metadata
- **`uv.lock`**: Locked dependency versions
- **`.python-version`**: Python 3.12 specification
- **`.env.example`**: Environment variable template

### Frontend
- **`package.json`**: Node dependencies, scripts
- **`bun.lock`**: Locked dependency versions
- **`next.config.ts`**: Next.js configuration (API proxy, etc.)
- **`tsconfig.json`**: TypeScript compiler options
- **`components.json`**: shadcn/ui component configuration
- **`eslint.config.mjs`**: Linting rules
- **`postcss.config.mjs`**: PostCSS plugins (Tailwind CSS)

## Documentation

- **`README.md`**: Main project documentation
  - Features overview
  - Quick start guide
  - Dataset information
  - Scoring algorithm explanation
  - Future enhancements

- **`ML_PIPELINE.md`**: Comprehensive ML pipeline documentation
  - 6-stage pipeline architecture
  - Stage-by-stage details
  - Error handling strategies
  - Performance benchmarks
  - API response formats
  - Testing edge cases

- **`DEPLOYMENT.md`**: Deployment guide
  - Local development setup
  - Production deployment
  - Environment variables
  - Troubleshooting

## Git Ignored Files

### Backend (.gitignore)
- Python cache (`__pycache__/`, `*.pyc`)
- Virtual environment (`.venv/`, `venv/`, `env/`)
- Environment files (`.env`, `.env.local`)
- Build artifacts (`*.egg-info/`, `dist/`, `build/`)

### Frontend (.gitignore)
- Node modules (`node_modules/`)
- Next.js build (`.next/`, `out/`)
- TypeScript build (`*.tsbuildinfo`)
- Environment files (`.env.local`, `.env.*.local`)

### Project-wide (.gitignore)
- IDE files (`.vscode/`, `.idea/`, `*.swp`)
- OS files (`.DS_Store`)
- Log files (`*.log`)
- Test coverage (`.coverage`, `.pytest_cache/`)

## Key Technologies

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **Pandas**: Data manipulation and CSV processing
- **Uvicorn**: ASGI server
- **UV**: Fast Python package manager

### Frontend
- **Next.js 15**: React framework with App Router
- **shadcn/ui**: Component library
- **Tailwind CSS**: Utility-first CSS
- **Lucide React**: Icon library
- **Bun**: JavaScript runtime and package manager
- **Sonner**: Toast notifications

## Development Workflow

1. **Backend Development**
   ```bash
   cd backend
   uv sync                    # Install dependencies
   uv run python main.py      # Start server (port 8000)
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   bun install                # Install dependencies
   bun run dev                # Start dev server (port 3000)
   ```

3. **Testing**
   - Upload CSV files through UI
   - Test with sample-leads.csv (200 leads)
   - Test with kaggle_leads.csv (889 leads)
   - Test with leads_10k.csv (10K leads)
   - Check processing progress UI
   - Verify error handling

4. **Building for Production**
   ```bash
   # Backend: No build step needed
   # Frontend:
   cd frontend
   bun run build              # Creates .next/ production build
   ```

## Performance Benchmarks

| Dataset Size | Processing Time | Throughput |
|--------------|----------------|------------|
| 200 leads | 0.15s | 1,333 leads/sec |
| 889 leads | 0.60s | 1,481 leads/sec |
| 10,000 leads | 1.24s | 8,064 leads/sec |

## ML Pipeline Stages

1. **Data Validation**: File format, encoding, required fields, email validation
2. **Data Cleaning**: Normalization, standardization, deduplication
3. **Feature Extraction**: DataFrame to Lead objects conversion
4. **Data Enrichment**: Company size, industry classification, LinkedIn URLs
5. **Lead Scoring**: Rule-based ML scoring (0-100 scale)
6. **Quality Check**: Final validation, metrics generation

See `ML_PIPELINE.md` for detailed documentation.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload-leads` | POST | Upload CSV and process through ML pipeline |
| `/api/leads` | GET | Get all leads (with pagination) |
| `/api/export` | GET | Export leads to CSV |
| `/api/processing-progress` | GET | Get real-time pipeline progress |
| `/api/leads` | DELETE | Clear all leads from storage |

## Future Enhancements

See `README.md` for comprehensive list of 45+ planned features including:
- Database integration (PostgreSQL/MongoDB)
- Authentication (JWT/OAuth2)
- Real API integrations (Clearbit, Hunter.io, LinkedIn)
- Advanced analytics dashboard
- Machine learning enhancements
- CRM integrations (Salesforce, HubSpot)
- Performance optimizations (Redis, Celery)
- Testing & monitoring
- DevOps & CI/CD

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - See LICENSE file for details

## Support

For questions or issues, please open an issue on GitHub.

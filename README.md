# AI Lead Scoring & Enrichment Dashboard

> **Transform raw leads into actionable insights with AI-powered scoring and automated enrichment**

A professional full-stack application designed for Caprae Capital's Full Stack Developer challenge that demonstrates AI-driven business intelligence for lead generation and prioritization.

## 🎯 Business Context & Problem Statement

Raw lead data from scrapers and online sources lacks **prioritization, verification, and actionable context**. Sales and acquisition teams waste valuable time manually validating and ranking leads, often missing high-value opportunities buried in unstructured data.

**This dashboard solves that by:**
- ✅ Automatically enriching leads with company size, industry, LinkedIn profiles, and email validation
- ✅ Scoring leads 0-100 based on decision-making authority, company fit, and data quality
- ✅ Providing intuitive filtering, sorting, and export capabilities for CRM integration
- ✅ Delivering immediate visual insights through color-coded scores and statistics

## 🚀 Key Features

| Feature | Description | Business Value |
|---------|-------------|----------------|
| **CSV Upload** | Bulk import leads from any source | Seamless integration with existing tools |
| **Auto-Enrichment** | Company size, industry classification, LinkedIn URLs, email validation | Adds missing context automatically |
| **AI Scoring** | Transparent 0-100 score based on job title, company size, industry match, email validity | Prioritizes high-value leads instantly |
| **Smart Filters** | Filter by industry, location, job title, minimum score | Find your ideal prospects fast |
| **Sortable Table** | Click any column to sort ascending/descending | Quick data exploration |
| **Color-Coded Scores** | Green (≥70), Yellow (40-69), Red (<40) | Instant visual prioritization |
| **Export to CRM** | Download enriched leads as CSV | Hand off to sales teams seamlessly |

## 📊 Scoring Logic

The dashboard uses a **transparent, rule-based scoring system** aligned with business priorities:

### Scoring Criteria (Total: 0-100 scale)

| Criteria | Points | Reasoning |
|----------|--------|-----------|
| **Job Title** | 0-10 | CEO/Founder (10), VP/Director (7), Manager (5), Other (3) |
| **Company Size** | 0-10 | 1000+ employees (10), 200-1000 (7), 50-200 (5), <50 (3) |
| **Industry Match** | 0-10 | Target industries like tech/finance (10), Related (5), Other (0) |
| **Email Validation** | -10 to +5 | Valid email (+5), Invalid email (-10) |

**Formula:**
```
Raw Score = JobTitle + CompanySize + IndustryMatch + EmailValidation
Normalized Score = ((Raw Score + 10) / 45) × 100
```

This creates a **0-100 scale** where:
- **70-100**: High-priority leads (decision-makers at target companies)
- **40-69**: Medium-priority leads (worth reviewing)
- **0-39**: Low-priority leads (may not be a good fit)

## 🏗️ Tech Stack

### Backend (FastAPI + Python)
- **FastAPI**: Modern, high-performance API framework
- **Pydantic**: Data validation and serialization
- **Pandas**: CSV processing and data manipulation
- **UV**: Fast Python package management

### Frontend (Next.js + shadcn/ui)
- **Next.js 15**: React framework with App Router
- **shadcn/ui**: Beautiful, accessible component library
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Modern icon library
- **Bun**: Ultra-fast JavaScript runtime

## 📁 Project Structure

```
AI-Lead-Scoring-and-Enrichment-Dashboard/
├── backend/
│   ├── src/
│   │   ├── models/lead.py           # Pydantic models
│   │   ├── routes/api.py            # API endpoints
│   │   ├── utils/
│   │   │   ├── enrichment.py        # Data enrichment logic
│   │   │   └── scoring.py           # AI scoring algorithm
│   │   └── app.py                   # FastAPI app
│   ├── main.py                      # Entry point
│   ├── sample-leads.csv             # Demo data
│   └── pyproject.toml               # Dependencies
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx             # Main dashboard
│   │   ├── components/
│   │   │   ├── LeadTable.tsx        # Sortable table
│   │   │   ├── FiltersPanel.tsx     # Filter controls
│   │   │   ├── ScoreBadge.tsx       # Color-coded badges
│   │   │   └── ui/                  # shadcn/ui components
│   └── package.json                 # Dependencies
│
└── README.md                        # This file
```

## 🚦 Quick Start

### Prerequisites
- **Python 3.12+** with UV package manager
- **Node.js 18+** with Bun runtime
- **Git** for version control

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AI-Lead-Scoring-and-Enrichment-Dashboard
```

### 2. Start the Backend
```bash
cd backend
uv sync                    # Install dependencies
uv run python main.py      # Start FastAPI server on port 8000
```

Backend will be available at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### 3. Start the Frontend
```bash
cd frontend
bun install                # Install dependencies
bun run dev                # Start Next.js dev server on port 3000
```

Frontend will be available at: `http://localhost:3000`

### 4. Try It Out!
1. **Load Sample Data**: Click "Load Sample" to see pre-enriched leads
2. **Upload Your Own**: Use the provided `backend/sample-leads.csv` or create your own
3. **Filter & Sort**: Use the sidebar to filter leads and click column headers to sort
4. **Export**: Download enriched leads as CSV for your CRM

## 📝 CSV Format

Your input CSV should have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| `name` | ✅ | Lead's full name |
| `email` | ✅ | Email address |
| `company` | ✅ | Company name |
| `job_title` | ✅ | Job title/role |
| `location` | ❌ | City, State/Country |
| `industry` | ❌ | Industry (will auto-classify if missing) |

Example:
```csv
name,email,company,job_title,location,industry
Sarah Johnson,sarah@techventures.com,TechVentures,CEO,San Francisco CA,
Michael Chen,michael@bigcorp.com,BigCorp Inc,VP of Sales,New York NY,finance
```

## 🎓 Why This Project for Caprae Capital?

This dashboard aligns perfectly with Caprae's evaluation criteria:

| Criterion | How This Project Delivers |
|-----------|---------------------------|
| **Business Use Case** | Solves real acquisition/sales pain point: lead prioritization |
| **UX/UI** | Clean, professional interface with immediate insights |
| **Technicality** | Full-stack with data enrichment, scoring algorithms, CSV processing |
| **Design** | Modern shadcn/ui components, responsive layout, visual hierarchy |
| **Creativity** | Adds AI scoring + enrichment layer on top of basic scraping tools |

**Business Impact:**
- Saves **hours per week** in manual lead qualification
- Increases **conversion rates** by focusing on high-scoring leads first
- Demonstrates **AI-readiness** for portfolio companies
- Shows understanding of **post-acquisition value creation**

## 🔄 API Endpoints

### `POST /api/upload-leads`
Upload CSV file, enrich, and score leads
- **Input**: CSV file (multipart/form-data)
- **Output**: Array of scored leads with enrichment data

### `GET /api/leads`
Get all scored leads (or sample data if none uploaded)
- **Output**: Array of scored leads

### `GET /api/export`
Download scored leads as CSV
- **Output**: CSV file download

### `DELETE /api/leads`
Clear all leads from storage
- **Output**: Success message

## 🛠️ Development

### Backend
```bash
cd backend
uv add <package>           # Add new dependency
uv run pytest              # Run tests (if added)
```

### Frontend
```bash
cd frontend
bun add <package>          # Add new dependency
bun run build              # Production build
bunx shadcn add <component> # Add shadcn/ui component
```

## 📈 Future Enhancements

- [ ] **Real API Integration**: Connect to Clearbit, Hunter.io for live enrichment
- [ ] **Database**: PostgreSQL for persistent storage
- [ ] **Authentication**: User accounts and saved searches
- [ ] **ML Model**: Train on historical conversion data for better scoring
- [ ] **Bulk Actions**: Email outreach directly from dashboard
- [ ] **Analytics**: Charts showing lead quality trends over time
- [ ] **Webhooks**: Real-time CRM synchronization

## 📜 License

MIT License - feel free to use this for your own projects!

---

**Built with ❤️ for Caprae Capital's Full Stack Developer Challenge**

*Demonstrating AI-driven insights, modern full-stack development, and business value creation*

## 🚀 Features

- **CSV Upload & Export**: Bulk import raw leads and download enriched results instantly
- **Automated Enrichment**: Append company size, industry, LinkedIn URLs, and email validation
- **Explainable AI Scoring**: Rule-based scoring (0–100) aligned with decision-maker impact and data quality
- **Interactive Dashboard**: Sortable table, filters, and high-level stats for rapid prioritization
- **Real-time Feedback**: Immediate results with score badges and validation indicators
- **Responsive Design**: Works across desktop, tablet, and mobile

## 🛠 Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Shadcn/UI** - Modern UI components
- **Tailwind CSS** - Utility-first CSS framework
- **Bun** - Fast JavaScript runtime and package manager

### Backend
- **FastAPI** - High-performance Python web framework
- **Pydantic** - Data validation and serialization
- **Pandas** - Data manipulation and CSV processing
- **Uvicorn** - ASGI server
- **uv** - Fast Python package manager

## 📋 Prerequisites

- **Node.js** (for Bun runtime) or **Bun** directly
- **Python 3.12+**
- **uv** (Python package manager)
- **Git**

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jainam1673/AI-Lead-Scoring-and-Enrichment-Dashboard.git
   cd AI-Lead-Scoring-and-Enrichment-Dashboard
   ```

2. **Backend Setup**
   ```bash
   cd backend
   uv sync
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   bun install
   ```

## 🚀 Running the Application

### Development Mode

1. **Start the Backend** (Terminal 1)
   ```bash
   cd backend
   uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Frontend** (Terminal 2)
   ```bash
   cd frontend
   bun run dev
   ```
   The dashboard will be available at `http://localhost:3000`

### Production Build

1. **Build Frontend**
   ```bash
   cd frontend
   bun run build
   bun run start
   ```

2. **Run Backend**
   ```bash
   cd backend
   uv run uvicorn src.app:app --host 0.0.0.0 --port 8000
   ```

## 📖 Usage

1. **Access the Dashboard**: Open `http://localhost:3000` in your browser
2. **Upload Leads**: Click "Choose File" and select a CSV file with lead data
3. **Score Leads**: Click "Upload and Score" to process the leads
4. **View Results**: Scored leads appear in the table below
5. **Sample Data**: Use "Load Sample Leads" to see example data

### CSV Format

Your CSV file should include these columns:
- `name` - Lead's full name
- `email` - Email address
- `company` - Company name
- `job_title` - Job title/role
- `industry` (optional) - Industry sector
- `location` (optional) - Geographic location

Example CSV:
```csv
name,email,company,job_title,industry,location
John Doe,john@techcorp.com,TechCorp,CEO,Technology,San Francisco
Jane Smith,jane@startup.com,StartupInc,CTO,Software,New York
```

## 🔌 API Documentation

The backend provides RESTful APIs. When running, visit `http://localhost:8000/docs` for interactive API documentation.

### Endpoints

- `GET /` - Health check
- `GET /api/leads` - Get sample scored leads
- `POST /api/upload-leads` - Upload and score leads from CSV

### API Example

```bash
curl -X POST "http://localhost:8000/api/upload-leads" \
     -F "file=@leads.csv"
```

## 🤖 AI Scoring Model

The application uses a machine learning model trained on job title data to score leads from 0-1:

- **High scores** (0.8+): Executive roles (CEO, CTO, Founder)
- **Medium scores** (0.5-0.8): Technical/managerial roles
- **Low scores** (<0.5): Other positions

The model is a simple logistic regression classifier using TF-IDF vectorization of job titles.

## 🏗 Project Structure

```
AI-Lead-Scoring-and-Enrichment-Dashboard/
├── backend/
│   ├── src/
│   │   ├── app.py          # FastAPI application
│   │   ├── models/
│   │   │   └── lead.py     # Pydantic models
│   │   ├── routes/
│   │   │   └── api.py      # API endpoints
│   │   └── utils/
│   │       └── scoring.py  # AI scoring logic
│   ├── main.py             # Server entry point
│   ├── pyproject.toml      # Python dependencies
│   └── uv.lock             # Lock file
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx    # Main dashboard
│   │   │   └── layout.tsx  # App layout
│   │   ├── components/
│   │   │   └── ui/         # Shadcn components
│   │   └── lib/
│   │       └── utils.ts    # Utility functions
│   ├── package.json        # Node dependencies
│   └── bun.lock            # Lock file
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for Caprae Capital's evaluation process
- Uses open-source libraries and frameworks
- Inspired by modern lead management tools

## 📞 Support

For questions or issues, please open an issue on GitHub.

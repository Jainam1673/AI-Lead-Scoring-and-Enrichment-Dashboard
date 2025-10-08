# AI Lead Scoring and Enrichment Dashboard

A full-stack web application that demonstrates AI-powered lead scoring and enrichment for sales teams. Upload CSV files of potential leads, and get them automatically scored and enriched using machine learning models.

## 🚀 Features

- **CSV Upload**: Securely upload lead data in CSV format
- **AI Lead Scoring**: Machine learning model scores leads based on job titles and company data
- **Data Enrichment**: Automatic enrichment of lead information (planned for future)
- **Interactive Dashboard**: Clean, modern UI to view and manage scored leads
- **Real-time Processing**: Instant scoring and display of results
- **Responsive Design**: Works on desktop and mobile devices

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
- **Scikit-learn** - Machine learning library for scoring
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

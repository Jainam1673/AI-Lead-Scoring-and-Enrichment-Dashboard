# Frontend – AI Lead Scoring & Enrichment Dashboard

Modern Next.js dashboard built with shadcn/ui and Tailwind CSS for managing, filtering, and exporting enriched leads.

## 🎯 Overview

The interface delivers:
- CSV upload that posts leads to the FastAPI backend for enrichment and scoring
- Real-time statistics cards (total leads, average score, high-quality leads, valid emails)
- Sortable, filterable data table with color-coded score badges and LinkedIn links
- Sidebar filters for search, industry, location, and minimum score
- CSV export button that downloads enriched leads for CRM import

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Dashboard page
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Tailwind styles
│   ├── components/
│   │   ├── LeadTable.tsx         # Sortable, color-coded table
│   │   ├── FiltersPanel.tsx      # Filter controls
│   │   ├── ScoreBadge.tsx        # Score badge component
│   │   └── ui/                   # shadcn/ui primitives
│   └── lib/
│       └── utils.ts              # Utility helpers
├── public/                       # Static assets
├── package.json / bun.lockb      # Bun dependencies
└── next.config.ts                # Next.js configuration
```

## 🚀 Setup & Installation

### Prerequisites
- Node.js 18+
- [Bun](https://bun.sh) runtime
- Backend running at `http://localhost:8000` (or configure `NEXT_PUBLIC_API_URL`)

### Install Dependencies
```bash
bun install
```

### Run Development Server
```bash
bun run dev
```

The app is available at [http://localhost:3000](http://localhost:3000).

### Build & Serve Production Bundle
```bash
bun run build
bun run start
```

## 🔌 Backend Integration

The frontend communicates with the FastAPI backend via these endpoints:
- `POST /api/upload-leads` – Upload CSV, enrich, and score leads
- `GET /api/leads` – Fetch current scored leads (with demo fallback)
- `GET /api/export` – Download enriched leads as CSV

Set `NEXT_PUBLIC_API_URL` in a `.env.local` file to override the default backend URL:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.example.com
```

## 📊 Key Components

### `LeadTable`
- Sort by clicking column headers (ascending → descending → reset)
- Displays company size, industry, email validity, and LinkedIn links
- Uses `ScoreBadge` for visual priority cues (green ≥70, yellow ≥40, red otherwise)

### `FiltersPanel`
- Search across name, company, and job title
- Filter by industry substring and location substring
- Slider to constrain minimum score (0–100)

### `ScoreBadge`
- Encapsulates badge coloring logic based on numeric score
- Reusable across future analytics cards

## 🧪 QA Checklist

- [ ] Run `bun run dev` (verify dashboard loads)
- [ ] Click **Load Sample** to fetch demo data
- [ ] Upload `backend/sample-leads.csv` and confirm enrichment results
- [ ] Sort by Score, Company, Job Title (asc/desc/reset)
- [ ] Filter by industry/location and adjust minimum score slider
- [ ] Click LinkedIn icons (open in new tab)
- [ ] Export CSV and confirm downloaded data matches table

## 🛠️ Extending the UI

- Add shadcn/ui components via `bunx shadcn@latest add <component>`
- Introduce charts (e.g., `@tanstack/react-charts`) for score distributions
- Implement dark mode by toggling Tailwind `dark` class
- Persist filters in URL query parameters for sharable views

## 📄 License

MIT License. Part of the AI Lead Scoring & Enrichment Dashboard submission for Caprae Capital.

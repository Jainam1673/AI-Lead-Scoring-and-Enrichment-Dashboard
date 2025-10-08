# Backend for AI Lead Scoring and Enrichment Dashboard

This is the Python backend using FastAPI, managed with uv.

## Setup

1. Ensure uv is installed.
2. Install dependencies: `uv sync`
3. Run the server: `uv run main.py`

## API Endpoints

- `GET /api/leads`: Get mock scored leads
- `POST /api/upload-leads`: Upload CSV file to score leads

## Features

- AI-based lead scoring using scikit-learn
- CSV upload and processing
- CORS enabled for frontend
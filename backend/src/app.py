from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.api import router
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get CORS origins from environment or use defaults
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app = FastAPI(
    title="AI Lead Scoring & Enrichment API",
    version="1.0.0",
    description="Automated lead enrichment and AI-powered scoring for sales teams",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AI Lead Scoring & Enrichment API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "upload": "/api/upload-leads",
            "leads": "/api/leads",
            "export": "/api/export",
            "clear": "/api/leads"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ai-lead-scoring-api",
        "version": "1.0.0"
    }
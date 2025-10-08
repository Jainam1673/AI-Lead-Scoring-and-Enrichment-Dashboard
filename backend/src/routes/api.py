from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import io
import json
from ..models.lead import Lead, ScoredLead
from ..utils.scoring import score_leads

router = APIRouter()

@router.post("/upload-leads", response_model=list[ScoredLead])
async def upload_leads(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        return JSONResponse(status_code=400, content={"error": "Only CSV files allowed"})
    
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    leads = []
    for _, row in df.iterrows():
        lead = Lead(
            name=row.get('name', ''),
            email=row.get('email', ''),
            company=row.get('company', ''),
            job_title=row.get('job_title', ''),
            industry=row.get('industry'),
            location=row.get('location')
        )
        leads.append(lead)
    
    scored_leads = score_leads(leads)
    return scored_leads

@router.get("/leads", response_model=list[ScoredLead])
async def get_leads():
    # Mock data for now
    leads = [
        ScoredLead(id=1, name="John Doe", email="john@company.com", company="TechCorp", job_title="CEO", score=0.9),
        ScoredLead(id=2, name="Jane Smith", email="jane@startup.com", company="StartupInc", job_title="CTO", score=0.8)
    ]
    return leads
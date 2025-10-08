from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import pandas as pd
import io
import json
from typing import List
from ..models.lead import Lead, ScoredLead
from ..utils.scoring import score_leads
from ..utils.enrichment import enrich_leads

router = APIRouter()

# In-memory storage for demo (in production, use a database)
leads_storage: List[ScoredLead] = []


@router.post("/upload-leads", response_model=list[ScoredLead])
async def upload_leads(file: UploadFile = File(...)):
    """
    Upload CSV file with leads, enrich them, and score them.
    Expected CSV columns: name, email, company, job_title, location (optional), industry (optional)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Validate required columns
        required_cols = ['name', 'email', 'company', 'job_title']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )
        
        # Parse CSV into Lead objects
        leads = []
        for idx, row in df.iterrows():
            try:
                lead = Lead(
                    id=int(idx) + 1 if isinstance(idx, (int, float)) else None,
                    name=str(row.get('name', '')),
                    email=str(row.get('email', '')),
                    company=str(row.get('company', '')),
                    job_title=str(row.get('job_title', '')),
                    industry=str(row.get('industry')) if pd.notna(row.get('industry')) else None,
                    location=str(row.get('location')) if pd.notna(row.get('location')) else None,
                )
                leads.append(lead)
            except Exception as e:
                print(f"Error parsing row {idx}: {e}")
                continue
        
        if not leads:
            raise HTTPException(status_code=400, detail="No valid leads found in CSV")
        
        # Step 1: Enrich leads
        enriched_leads = enrich_leads(leads)
        
        # Step 2: Score enriched leads
        scored_leads = score_leads(enriched_leads)
        
        # Store in memory for later export
        global leads_storage
        leads_storage = scored_leads
        
        return scored_leads
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/leads", response_model=list[ScoredLead])
async def get_leads():
    """
    Get all scored leads from storage.
    Returns sample data if no leads uploaded yet.
    """
    if not leads_storage:
        # Return sample enriched and scored leads for demo
        sample_leads = [
            Lead(
                id=1,
                name="Sarah Johnson",
                email="sarah.johnson@techventures.com",
                company="TechVentures",
                job_title="CEO",
                location="San Francisco, CA"
            ),
            Lead(
                id=2,
                name="Michael Chen",
                email="michael@bigcorp.com",
                company="BigCorp Inc",
                job_title="VP of Sales",
                location="New York, NY"
            ),
            Lead(
                id=3,
                name="Emily Rodriguez",
                email="emily@invalid.test",
                company="StartupLabs",
                job_title="Marketing Manager",
                location="Austin, TX"
            ),
        ]
        
        enriched = enrich_leads(sample_leads)
        return score_leads(enriched)
    
    return leads_storage


@router.get("/export")
async def export_leads():
    """
    Export scored leads as CSV file for download.
    """
    if not leads_storage:
        raise HTTPException(status_code=404, detail="No leads available to export")
    
    # Convert scored leads to DataFrame
    data = []
    for lead in leads_storage:
        data.append({
            "name": lead.name,
            "email": lead.email,
            "company": lead.company,
            "job_title": lead.job_title,
            "industry": lead.industry,
            "location": lead.location,
            "company_size": lead.company_size,
            "linkedin_url": lead.linkedin_url,
            "email_valid": lead.email_valid,
            "score": lead.score,
            "score_breakdown": json.dumps(lead.score_breakdown),
        })
    
    df = pd.DataFrame(data)
    
    # Convert to CSV
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scored_leads.csv"}
    )
    
    return response


@router.delete("/leads")
async def clear_leads():
    """
    Clear all leads from storage.
    """
    global leads_storage
    leads_storage = []
    return {"message": "All leads cleared"}
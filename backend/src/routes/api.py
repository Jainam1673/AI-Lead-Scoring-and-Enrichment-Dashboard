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
    Returns sample data from CSV if no leads uploaded yet.
    """
    if not leads_storage:
        # Load sample data from CSV file
        import os
        from pathlib import Path
        
        # Get the path to sample-leads.csv
        current_dir = Path(__file__).parent.parent.parent
        sample_csv_path = current_dir / "sample-leads.csv"
        
        if not sample_csv_path.exists():
            raise HTTPException(status_code=404, detail="Sample data file not found")
        
        try:
            # Read CSV
            df = pd.read_csv(sample_csv_path)
            
            # Parse leads
            sample_leads = []
            for idx, row in df.iterrows():
                try:
                    lead_id = int(idx) + 1 if isinstance(idx, (int, float)) else len(sample_leads) + 1
                    lead = Lead(
                        id=lead_id,
                        name=str(row.get('name', '')),
                        email=str(row.get('email', '')),
                        company=str(row.get('company', '')),
                        job_title=str(row.get('job_title', '')),
                        industry=str(row.get('industry')) if pd.notna(row.get('industry')) else None,
                        location=str(row.get('location')) if pd.notna(row.get('location')) else None,
                    )
                    sample_leads.append(lead)
                except Exception as e:
                    print(f"Error parsing row {idx}: {e}")
                    continue
            
            # Enrich and score
            enriched = enrich_leads(sample_leads)
            return score_leads(enriched)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading sample data: {str(e)}")
    
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
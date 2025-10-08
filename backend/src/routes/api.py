from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import pandas as pd
import io
import json
import logging
from typing import List
from ..models.lead import Lead, ScoredLead
from ..utils.scoring import score_leads
from ..utils.enrichment import enrich_leads

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for demo (in production, use a database)
leads_storage: List[ScoredLead] = []

# Configuration
MAX_UPLOAD_SIZE_MB = 50
MAX_LEADS_PER_UPLOAD = 50000


@router.post("/upload-leads", response_model=list[ScoredLead])
async def upload_leads(file: UploadFile = File(...)):
    """
    Upload CSV file with leads, enrich them, and score them.
    Expected CSV columns: name, email, company, job_title, location (optional), industry (optional)
    """
    logger.info(f"Upload request received: {file.filename}")
    
    if not file.filename.endswith('.csv'):
        logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if file_size_mb > MAX_UPLOAD_SIZE_MB:
            logger.warning(f"File too large: {file_size_mb:.2f}MB")
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE_MB}MB"
            )
        
        logger.info(f"Processing file: {file_size_mb:.2f}MB")
        df = pd.read_csv(io.BytesIO(contents))
        
        # Validate required columns
        required_cols = ['name', 'email', 'company', 'job_title']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing columns: {missing_cols}")
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )
        
        # Check lead count
        if len(df) > MAX_LEADS_PER_UPLOAD:
            logger.warning(f"Too many leads: {len(df)}")
            raise HTTPException(
                status_code=413,
                detail=f"Too many leads. Maximum is {MAX_LEADS_PER_UPLOAD} per upload"
            )
        
        logger.info(f"Parsing {len(df)} leads from CSV")
        
        # Parse CSV into Lead objects
        leads = []
        errors = []
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
                error_msg = f"Row {idx}: {str(e)}"
                logger.warning(f"Error parsing row: {error_msg}")
                errors.append(error_msg)
                continue
        
        if not leads:
            logger.error("No valid leads parsed from CSV")
            raise HTTPException(
                status_code=400,
                detail=f"No valid leads found in CSV. Errors: {errors[:5]}"
            )
        
        logger.info(f"Successfully parsed {len(leads)} leads ({len(errors)} errors)")
        
        # Step 1: Enrich leads
        logger.info("Enriching leads...")
        enriched_leads = enrich_leads(leads)
        
        # Step 2: Score enriched leads
        logger.info("Scoring leads...")
        scored_leads = score_leads(enriched_leads)
        
        # Store in memory for later export
        global leads_storage
        leads_storage = scored_leads
        
        logger.info(f"Successfully processed {len(scored_leads)} leads")
        return scored_leads
        
    except pd.errors.EmptyDataError:
        logger.error("Empty CSV file uploaded")
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error processing file")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/leads", response_model=list[ScoredLead])
async def get_leads(limit: int | None = None, offset: int = 0):
    """
    Get scored leads from storage with optional pagination.
    
    Args:
        limit: Maximum number of leads to return (optional)
        offset: Number of leads to skip (default: 0)
    
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
            scored = score_leads(enriched)
            
            # Apply pagination
            if limit is not None:
                return scored[offset:offset + limit]
            return scored[offset:]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading sample data: {str(e)}")
    
    # Apply pagination to stored leads
    if limit is not None:
        return leads_storage[offset:offset + limit]
    return leads_storage[offset:]


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
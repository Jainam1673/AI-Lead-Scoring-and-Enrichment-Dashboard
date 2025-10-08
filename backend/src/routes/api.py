from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import pandas as pd
import io
import json
import logging
from typing import List, Dict, Any
from ..models.lead import Lead, ScoredLead
from ..utils.scoring import score_leads
from ..utils.enrichment import enrich_leads
from ..utils.validation import validate_csv_file, DataValidator
from ..utils.cleaning import clean_lead_data
from ..utils.pipeline import ProcessingPipeline, ProcessingStage

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

# Global pipeline instance for progress tracking
current_pipeline: ProcessingPipeline | None = None


@router.post("/upload-leads", response_model=List[ScoredLead])
async def upload_leads(file: UploadFile = File(...)):
    """
    Upload CSV file with leads, process through ML pipeline, and return scored leads.
    Expected CSV columns: name, email, company, job_title, location (optional), industry (optional)
    
    Processing stages:
    1. File validation (size, format, encoding)
    2. Data validation (required fields, email format, data quality)
    3. Data cleaning (normalization, deduplication, standardization)
    4. Feature extraction (parse company size, extract domain info)
    5. Data enrichment (company size, industry classification)
    6. Lead scoring (rule-based ML scoring algorithm)
    7. Quality check (final validation, quality metrics)
    """
    global current_pipeline
    
    logger.info(f"Upload request received: {file.filename}")
    
    # Basic file validation
    if not file.filename.endswith('.csv'):
        logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed. Please upload a file with .csv extension."
        )
    
    try:
        # Read file contents
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if file_size_mb > MAX_UPLOAD_SIZE_MB:
            logger.warning(f"File too large: {file_size_mb:.2f}MB")
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({file_size_mb:.1f}MB). Maximum size is {MAX_UPLOAD_SIZE_MB}MB. Please split your file or contact support."
            )
        
        logger.info(f"Processing file: {file_size_mb:.2f}MB")
        
        # Try different encodings if UTF-8 fails
        try:
            df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(io.BytesIO(contents), encoding='latin-1')
                logger.warning("File decoded using latin-1 encoding")
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unable to decode CSV file. Please ensure it's properly encoded (UTF-8 or Latin-1). Error: {str(e)}"
                )
        
        # Check if CSV has any data
        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty. Please upload a file with lead data."
            )
        
        # Check lead count
        if len(df) > MAX_LEADS_PER_UPLOAD:
            logger.warning(f"Too many leads: {len(df)}")
            raise HTTPException(
                status_code=413,
                detail=f"Too many leads ({len(df):,}). Maximum is {MAX_LEADS_PER_UPLOAD:,} per upload. Please split your file into smaller batches."
            )
        
        logger.info(f"CSV loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        
        # Initialize processing pipeline
        current_pipeline = ProcessingPipeline()
        
        # Define pipeline stage functions
        def validation_stage(data: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, Any]]:
            """Stage 1: Validate data"""
            validation_result = validate_csv_file(data)
            
            if not validation_result.is_valid:
                error_message = "Data validation failed:\n" + "\n".join(validation_result.errors)
                raise Exception(error_message)
            
            metadata = {
                'records_processed': len(data),
                'records_succeeded': validation_result.stats.get('valid_rows', 0),
                'records_failed': validation_result.stats.get('invalid_rows', 0),
                'warnings': validation_result.warnings,
                'errors': validation_result.errors,
                'validation_stats': validation_result.stats
            }
            
            return data, metadata
        
        def cleaning_stage(data: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, Any]]:
            """Stage 2: Clean and normalize data"""
            original_count = len(data)
            cleaned_data = clean_lead_data(data)
            final_count = len(cleaned_data)
            
            metadata = {
                'records_processed': original_count,
                'records_succeeded': final_count,
                'records_failed': original_count - final_count,
                'warnings': [f"Removed {original_count - final_count} duplicate records"] if original_count != final_count else [],
                'errors': []
            }
            
            return cleaned_data, metadata
        
        def feature_extraction_stage(data: pd.DataFrame) -> tuple[List[Lead], Dict[str, Any]]:
            """Stage 3: Extract features and convert to Lead objects"""
            leads = []
            errors = []
            
            for idx, row in data.iterrows():
                try:
                    lead = Lead(
                        id=int(idx) + 1,
                        name=str(row.get('name', '')),
                        email=str(row.get('email', '')),
                        company=str(row.get('company', '')),
                        job_title=str(row.get('job_title', '')),
                        industry=str(row.get('industry')) if pd.notna(row.get('industry')) else None,
                        location=str(row.get('location')) if pd.notna(row.get('location')) else None,
                        company_size=str(row.get('company_size')) if pd.notna(row.get('company_size')) else None,
                    )
                    leads.append(lead)
                except Exception as e:
                    error_msg = f"Row {idx}: {str(e)}"
                    logger.warning(f"Error parsing row: {error_msg}")
                    errors.append(error_msg)
                    continue
            
            metadata = {
                'records_processed': len(data),
                'records_succeeded': len(leads),
                'records_failed': len(errors),
                'warnings': errors[:10] if errors else [],  # Show first 10 errors as warnings
                'errors': []
            }
            
            if not leads:
                raise Exception(f"No valid leads extracted. Errors: {errors[:5]}")
            
            return leads, metadata
        
        def enrichment_stage(data: List[Lead]) -> tuple[List[Lead], Dict[str, Any]]:
            """Stage 4: Enrich lead data"""
            try:
                enriched_leads = enrich_leads(data)
                
                metadata = {
                    'records_processed': len(data),
                    'records_succeeded': len(enriched_leads),
                    'records_failed': len(data) - len(enriched_leads),
                    'warnings': [],
                    'errors': []
                }
                
                return enriched_leads, metadata
            except Exception as e:
                logger.error(f"Enrichment failed: {str(e)}")
                # Continue with partial data if enrichment fails
                metadata = {
                    'records_processed': len(data),
                    'records_succeeded': len(data),
                    'records_failed': 0,
                    'warnings': [f"Enrichment partially failed: {str(e)}. Continuing with available data."],
                    'errors': []
                }
                return data, metadata
        
        def scoring_stage(data: List[Lead]) -> tuple[List[ScoredLead], Dict[str, Any]]:
            """Stage 5: Score leads"""
            scored_leads = score_leads(data)
            
            # Calculate score distribution
            scores = [lead.score for lead in scored_leads]
            avg_score = sum(scores) / len(scores) if scores else 0
            high_quality = len([s for s in scores if s >= 70])
            
            metadata = {
                'records_processed': len(data),
                'records_succeeded': len(scored_leads),
                'records_failed': 0,
                'warnings': [],
                'errors': [],
                'score_stats': {
                    'average_score': avg_score,
                    'high_quality_leads': high_quality,
                    'high_quality_percentage': (high_quality / len(scores) * 100) if scores else 0
                }
            }
            
            return scored_leads, metadata
        
        def quality_check_stage(data: List[ScoredLead]) -> tuple[List[ScoredLead], Dict[str, Any]]:
            """Stage 6: Final quality check"""
            # Validate final data
            valid_leads = [lead for lead in data if lead.email and lead.score is not None]
            
            metadata = {
                'records_processed': len(data),
                'records_succeeded': len(valid_leads),
                'records_failed': len(data) - len(valid_leads),
                'warnings': [],
                'errors': []
            }
            
            return valid_leads, metadata
        
        # Execute pipeline
        try:
            pipeline_result = current_pipeline.execute(
                df=df,
                validation_func=validation_stage,
                cleaning_func=cleaning_stage,
                feature_extraction_func=feature_extraction_stage,
                enrichment_func=enrichment_stage,
                scoring_func=scoring_stage,
                quality_check_func=quality_check_stage
            )
            
            if not pipeline_result.success:
                raise Exception("Pipeline execution failed")
            
            # Store in memory for later export
            global leads_storage
            leads_storage = pipeline_result.data
            
            logger.info(f"Pipeline completed: {pipeline_result.output_records} leads processed in {pipeline_result.total_duration_seconds:.2f}s")
            logger.info(f"Quality Report: {pipeline_result.success_rate:.1f}% success rate, {len(pipeline_result.progress.warnings)} warnings, {len(pipeline_result.progress.errors)} errors")
            
            # Return leads array for backward compatibility with frontend
            # Quality report is logged but not returned to avoid breaking frontend
            return pipeline_result.data
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Processing pipeline failed: {str(e)}"
            )
        
    except pd.errors.EmptyDataError:
        logger.error("Empty CSV file uploaded")
        raise HTTPException(
            status_code=400,
            detail="CSV file is empty or malformed. Please check your file and try again."
        )
    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Unable to parse CSV file. Please ensure it's properly formatted. Error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error processing file")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while processing your file. Please try again or contact support. Error: {str(e)}"
        )


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
    leads_to_export = leads_storage
    
    # If no leads in storage, load and use sample data
    if not leads_to_export:
        logger.info("No leads in storage, loading sample data for export")
        import os
        from pathlib import Path
        
        # Get the path to sample-leads.csv
        current_dir = Path(__file__).parent.parent.parent
        sample_csv_path = current_dir / "sample-leads.csv"
        
        if not sample_csv_path.exists():
            raise HTTPException(status_code=404, detail="No leads available to export")
        
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
                    logger.warning(f"Error parsing row {idx}: {e}")
                    continue
            
            # Enrich and score
            enriched = enrich_leads(sample_leads)
            leads_to_export = score_leads(enriched)
            logger.info(f"Exporting {len(leads_to_export)} sample leads")
        except Exception as e:
            logger.exception("Error loading sample data for export")
            raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")
    else:
        logger.info(f"Exporting {len(leads_to_export)} uploaded leads")
    
    # Convert scored leads to DataFrame
    data = []
    for lead in leads_to_export:
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


@router.get("/processing-progress")
async def get_processing_progress():
    """
    Get current processing progress for active pipeline.
    Returns progress information including stage, percentage, and statistics.
    """
    global current_pipeline
    
    if not current_pipeline:
        return {
            "status": "idle",
            "message": "No active processing"
        }
    
    progress = current_pipeline.get_progress()
    
    return {
        "status": "processing",
        "current_stage": progress.current_stage,
        "current_stage_status": progress.current_stage_status,
        "progress_percentage": progress.progress_percentage,
        "total_records": progress.total_records,
        "processed_records": progress.processed_records,
        "successful_records": progress.successful_records,
        "failed_records": progress.failed_records,
        "warnings_count": len(progress.warnings),
        "errors_count": len(progress.errors),
        "stage_results": [
            {
                "stage": result.stage,
                "status": result.status,
                "duration": result.duration_seconds,
                "records_processed": result.records_processed
            }
            for result in progress.stage_results
        ]
    }


@router.delete("/leads")
async def clear_leads():
    """
    Clear all leads from storage.
    """
    global leads_storage
    leads_storage = []
    return {"message": "All leads cleared"}
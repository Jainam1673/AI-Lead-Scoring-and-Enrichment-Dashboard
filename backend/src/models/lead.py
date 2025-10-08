from pydantic import BaseModel
from typing import Optional

class Lead(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    company: str
    job_title: str
    industry: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None  # e.g., "50-200", "200-1000", "1000+"
    linkedin_url: Optional[str] = None
    email_valid: Optional[bool] = None
    score: Optional[float] = None
    score_breakdown: Optional[dict] = None  # Details of how score was calculated

class LeadUpload(BaseModel):
    leads: list[Lead]

class ScoredLead(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    company: str
    job_title: str
    industry: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    linkedin_url: Optional[str] = None
    email_valid: Optional[bool] = None
    score: float
    score_breakdown: dict
    enriched: bool = True
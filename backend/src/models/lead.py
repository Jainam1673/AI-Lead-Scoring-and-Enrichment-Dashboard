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
    score: Optional[float] = None

class LeadUpload(BaseModel):
    leads: list[Lead]

class ScoredLead(Lead):
    score: float
    enriched_data: Optional[dict] = None
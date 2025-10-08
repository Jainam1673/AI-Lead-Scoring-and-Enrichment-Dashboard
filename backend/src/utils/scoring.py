"""
AI Lead Scoring Utilities

This module implements the comprehensive rule-based scoring system:
- Job Title Score (0-10): CEO/Founder=10, VP/Director=7, Manager=5, Other=3
- Company Size Score (0-10): 1000+=10, 200-1000=7, 50-200=5, <50=3
- Industry Match Score (0-10): Target industries=10, Related=5, Other=0
- Email Validation (-10/+5): Valid=+5, Invalid=-10

Final score is normalized to 0-100 scale with detailed breakdown.
"""

from typing import Dict, Tuple
from ..models.lead import Lead, ScoredLead

# Scoring weights and criteria
JOB_TITLE_SCORES = {
    "ceo": 10,
    "coo": 10,
    "cto": 10,
    "cfo": 10,
    "cmo": 10,
    "founder": 10,
    "co-founder": 10,
    "chief": 10,  # Chief Data Officer, Chief Revenue Officer, etc.
    "president": 9,
    "vp": 7,
    "vice president": 7,
    "director": 7,
    "head": 6,
    "manager": 5,
    "lead": 4,
    "senior": 3,
    "engineer": 3,
    "developer": 3,
    "analyst": 2,
    "coordinator": 2,
    "intern": 1,
    "assistant": 1,
}

COMPANY_SIZE_SCORES = {
    "5000+": 10,
    "1000-5000": 9,
    "1000+": 10,  # Legacy support
    "200-1000": 7,
    "50-200": 5,
    "10-50": 3,
}

# Target industries (customize for your Ideal Customer Profile)
TARGET_INDUSTRIES = ["tech", "finance", "healthcare"]
RELATED_INDUSTRIES = ["consulting", "ecommerce", "media"]

# Email validation impact
EMAIL_VALID_BONUS = 5
EMAIL_INVALID_PENALTY = -10


def score_job_title(job_title: str) -> Tuple[int, str]:
    """
    Score based on job title seniority and decision-making authority.
    
    Returns:
        Tuple of (score, reasoning)
    """
    if not job_title:
        return 1, "No job title provided"
    
    title_lower = job_title.lower()
    
    # Check for exact matches and patterns
    for keyword, score in sorted(JOB_TITLE_SCORES.items(), key=lambda x: -x[1]):
        if keyword in title_lower:
            return score, f"Job title '{job_title}' matches '{keyword}' pattern"
    
    # Default for unknown titles
    return 2, f"Job title '{job_title}' - standard score"


def score_company_size(company_size: str | None) -> Tuple[int, str]:
    """
    Score based on company size - larger companies often have bigger budgets.
    
    Returns:
        Tuple of (score, reasoning)
    """
    if not company_size:
        return 3, "Company size unknown - default score"
    
    score = COMPANY_SIZE_SCORES.get(company_size, 3)
    return score, f"Company size: {company_size}"


def score_industry_match(industry: str | None) -> Tuple[int, str]:
    """
    Score based on industry alignment with target market.
    
    Returns:
        Tuple of (score, reasoning)
    """
    if not industry:
        return 0, "Industry unknown"
    
    industry_lower = industry.lower()
    
    if industry_lower in TARGET_INDUSTRIES:
        return 10, f"Target industry: {industry}"
    elif industry_lower in RELATED_INDUSTRIES:
        return 5, f"Related industry: {industry}"
    else:
        return 0, f"Non-target industry: {industry}"


def score_email_validation(email_valid: bool | None) -> Tuple[int, str]:
    """
    Score based on email validation - penalize invalid emails heavily.
    
    Returns:
        Tuple of (score, reasoning)
    """
    if email_valid is None:
        return 0, "Email not validated"
    
    if email_valid:
        return EMAIL_VALID_BONUS, "Email validated successfully"
    else:
        return EMAIL_INVALID_PENALTY, "Email validation failed - likely invalid"


def calculate_lead_score(lead: Lead) -> Tuple[float, Dict]:
    """
    Calculate comprehensive lead score based on all criteria.
    
    Returns:
        Tuple of (normalized_score, breakdown_dict)
    """
    # Calculate individual scores
    job_score, job_reason = score_job_title(lead.job_title)
    size_score, size_reason = score_company_size(lead.company_size)
    industry_score, industry_reason = score_industry_match(lead.industry)
    email_score, email_reason = score_email_validation(lead.email_valid)
    
    # Calculate raw total (max possible: 10+10+10+5 = 35, min: 0+0+0-10 = -10)
    raw_score = job_score + size_score + industry_score + email_score
    
    # Normalize to 0-100 scale
    # Shift range from [-10, 35] to [0, 45], then scale to [0, 100]
    normalized_score = max(0, min(100, ((raw_score + 10) / 45) * 100))
    
    # Create detailed breakdown
    breakdown = {
        "total_score": round(normalized_score, 2),
        "job_title_score": job_score,
        "job_title_reason": job_reason,
        "company_size_score": size_score,
        "company_size_reason": size_reason,
        "industry_score": industry_score,
        "industry_reason": industry_reason,
        "email_score": email_score,
        "email_reason": email_reason,
        "raw_total": raw_score,
    }
    
    return normalized_score, breakdown


def score_leads(leads: list[Lead]) -> list[ScoredLead]:
    """
    Score multiple leads and return ScoredLead objects.
    
    Args:
        leads: List of Lead objects (should be enriched first)
        
    Returns:
        List of ScoredLead objects with scores and breakdowns
    """
    scored_leads = []
    
    for lead in leads:
        score, breakdown = calculate_lead_score(lead)
        
        scored_lead = ScoredLead(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            company=lead.company,
            job_title=lead.job_title,
            industry=lead.industry,
            location=lead.location,
            company_size=lead.company_size,
            linkedin_url=lead.linkedin_url,
            email_valid=lead.email_valid,
            score=score,
            score_breakdown=breakdown,
            enriched=True
        )
        
        scored_leads.append(scored_lead)
    
    return scored_leads
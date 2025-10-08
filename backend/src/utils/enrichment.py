"""
Data Enrichment Utilities for Lead Scoring Dashboard

This module provides functions to enrich lead data with additional context:
- Company size classification
- Industry categorization
- LinkedIn URL generation
- Email validation

In production, these would call external APIs (Clearbit, Hunter.io, etc.)
For demo purposes, we use intelligent mock data and pattern matching.
"""

import re
from typing import Optional

# Mock data for company size (in production, would call Clearbit/similar API)
COMPANY_SIZE_DATABASE = {
    "microsoft": "1000+",
    "google": "1000+",
    "amazon": "1000+",
    "apple": "1000+",
    "facebook": "1000+",
    "meta": "1000+",
    "netflix": "1000+",
    "salesforce": "1000+",
    "oracle": "1000+",
    "ibm": "1000+",
    "startup": "10-50",
    "ventures": "50-200",
    "technologies": "200-1000",
    "solutions": "50-200",
    "consulting": "50-200",
    "agency": "10-50",
    "studio": "10-50",
    "labs": "10-50",
}

# Industry classification based on company name/domain patterns
INDUSTRY_PATTERNS = {
    "tech": ["tech", "software", "saas", "cloud", "data", "ai", "digital"],
    "finance": ["capital", "bank", "finance", "invest", "venture", "fund"],
    "healthcare": ["health", "medical", "pharma", "biotech", "clinical"],
    "ecommerce": ["shop", "store", "retail", "commerce", "market"],
    "consulting": ["consult", "advisory", "services", "solutions"],
    "media": ["media", "marketing", "advertising", "agency", "creative"],
    "education": ["edu", "university", "academy", "learning", "training"],
    "manufacturing": ["manufacturing", "industrial", "factory", "production"],
}

# Target industries for scoring (customize based on your ICP)
TARGET_INDUSTRIES = ["tech", "finance", "healthcare"]


def classify_company_size(company_name: str) -> Optional[str]:
    """
    Classify company size based on company name patterns.
    In production, this would call an API like Clearbit.
    
    Returns: "10-50", "50-200", "200-1000", or "1000+"
    """
    company_lower = company_name.lower()
    
    # Check exact matches first
    for keyword, size in COMPANY_SIZE_DATABASE.items():
        if keyword in company_lower:
            return size
    
    # Default heuristics based on name patterns
    if "inc" in company_lower or "corporation" in company_lower or "corp" in company_lower:
        return "200-1000"
    elif "llc" in company_lower or "ltd" in company_lower:
        return "50-200"
    else:
        return "50-200"  # Default assumption


def classify_industry(company_name: str, existing_industry: Optional[str] = None) -> str:
    """
    Classify industry based on company name patterns.
    If industry is already provided, return it; otherwise infer.
    
    Returns: Industry category string
    """
    if existing_industry:
        return existing_industry
    
    company_lower = company_name.lower()
    
    for industry, patterns in INDUSTRY_PATTERNS.items():
        for pattern in patterns:
            if pattern in company_lower:
                return industry
    
    return "other"  # Default category


def generate_linkedin_url(name: str, company: str) -> str:
    """
    Generate a likely LinkedIn profile URL.
    In production, this would use LinkedIn API or a service like RocketReach.
    
    Returns: LinkedIn profile URL (mock format)
    """
    # Simple mock: convert name to linkedin format (firstname-lastname)
    name_parts = name.lower().strip().split()
    if len(name_parts) >= 2:
        linkedin_name = f"{name_parts[0]}-{name_parts[-1]}"
    else:
        linkedin_name = name_parts[0] if name_parts else "unknown"
    
    return f"https://linkedin.com/in/{linkedin_name}"


def validate_email(email: str) -> bool:
    """
    Validate email format and check for common invalid patterns.
    In production, would use Hunter.io or similar email verification API.
    
    Returns: True if email appears valid, False otherwise
    """
    # Basic regex validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False
    
    # Check for obviously fake domains
    invalid_domains = ["example.com", "test.com", "fake.com", "invalid.com", "none.com"]
    domain = email.split("@")[1].lower()
    if domain in invalid_domains:
        return False
    
    return True


def enrich_lead(lead) -> dict:
    """
    Enrich a single lead with additional data.
    
    Args:
        lead: Lead object to enrich
        
    Returns:
        Dictionary of enriched data fields
    """
    enriched = {}
    
    # Classify company size
    if not lead.company_size:
        enriched["company_size"] = classify_company_size(lead.company)
    
    # Classify or validate industry
    enriched["industry"] = classify_industry(lead.company, lead.industry)
    
    # Generate LinkedIn URL
    if not lead.linkedin_url:
        enriched["linkedin_url"] = generate_linkedin_url(lead.name, lead.company)
    
    # Validate email
    enriched["email_valid"] = validate_email(lead.email)
    
    return enriched


def enrich_leads(leads: list) -> list:
    """
    Enrich multiple leads with additional data.
    
    Args:
        leads: List of Lead objects
        
    Returns:
        List of leads with enriched data applied
    """
    enriched_leads = []
    
    for lead in leads:
        enriched_data = enrich_lead(lead)
        
        # Apply enriched data to lead
        lead.company_size = enriched_data.get("company_size", lead.company_size)
        lead.industry = enriched_data.get("industry", lead.industry)
        lead.linkedin_url = enriched_data.get("linkedin_url", lead.linkedin_url)
        lead.email_valid = enriched_data.get("email_valid", lead.email_valid)
        
        enriched_leads.append(lead)
    
    return enriched_leads

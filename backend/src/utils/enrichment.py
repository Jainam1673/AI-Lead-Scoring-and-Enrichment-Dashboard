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
# Based on real company data from 2024-2025
COMPANY_SIZE_DATABASE = {
    # Large Tech (5000+)
    "microsoft": "5000+",
    "google": "5000+",
    "amazon": "5000+",
    "apple": "5000+",
    "facebook": "5000+",
    "meta": "5000+",
    "netflix": "5000+",
    "salesforce": "5000+",
    "oracle": "5000+",
    "ibm": "5000+",
    "adobe": "5000+",
    "atlassian": "5000+",
    "servicenow": "5000+",
    "workday": "5000+",
    "uber": "5000+",
    "ebay": "5000+",
    "wayfair": "5000+",
    "shopify": "5000+",
    # Finance (5000+)
    "goldman sachs": "5000+",
    "morgan stanley": "5000+",
    "jpmorgan": "5000+",
    "citigroup": "5000+",
    "bank of america": "5000+",
    "wells fargo": "5000+",
    "american express": "5000+",
    "visa": "5000+",
    "mastercard": "5000+",
    "paypal": "5000+",
    # Healthcare (5000+)
    "unitedhealth": "5000+",
    "johnson & johnson": "5000+",
    "johnson": "5000+",
    "pfizer": "5000+",
    "cvs health": "5000+",
    "abbvie": "5000+",
    # Mid-size Tech (1000-5000)
    "stripe": "1000-5000",
    "databricks": "1000-5000",
    "snowflake": "1000-5000",
    "confluent": "1000-5000",
    "mongodb": "1000-5000",
    "hashicorp": "1000-5000",
    "datadog": "1000-5000",
    "twilio": "1000-5000",
    "zoom": "1000-5000",
    "dropbox": "1000-5000",
    "etsy": "1000-5000",
    "instacart": "1000-5000",
    "doordash": "1000-5000",
    "lyft": "1000-5000",
    "docusign": "1000-5000",
    "hubspot": "1000-5000",
    "zendesk": "1000-5000",
    "slack": "1000-5000",
    "asana": "1000-5000",
    "monday.com": "1000-5000",
    "gitlab": "1000-5000",
    "square": "1000-5000",
    "robinhood": "1000-5000",
    "coinbase": "1000-5000",
    "chime": "1000-5000",
    "moderna": "1000-5000",
    "oscar health": "1000-5000",
    "teladoc": "1000-5000",
    "one medical": "1000-5000",
    # Growing Startups (200-1000)
    "notion": "200-1000",
    "figma": "200-1000",
    "vercel": "200-1000",
    "anthropic": "200-1000",
    "scale ai": "200-1000",
    "hugging face": "200-1000",
    "weights & biases": "200-1000",
    "plaid": "200-1000",
    "23andme": "200-1000",
    "technologies": "200-1000",
    # Early Stage (50-200)
    "linear": "50-200",
    "supabase": "50-200",
    "replicate": "50-200",
    "startup": "10-50",
    "ventures": "50-200",
    "solutions": "50-200",
    "consulting": "50-200",
    "agency": "10-50",
    "studio": "10-50",
    "labs": "10-50",
}

# Industry classification based on company name/domain patterns
INDUSTRY_PATTERNS = {
    "tech": ["tech", "software", "saas", "cloud", "data", "ai", "digital", "platform", 
             "stripe", "databricks", "snowflake", "mongodb", "zoom", "slack", "notion", 
             "figma", "vercel", "gitlab", "atlassian", "servicenow", "docusign", "hubspot",
             "google", "microsoft", "amazon", "apple", "meta", "netflix", "oracle", "ibm", "adobe"],
    "finance": ["capital", "bank", "finance", "invest", "venture", "fund", "payment", "fintech",
                "goldman", "morgan", "jpmorgan", "citigroup", "wells fargo", "visa", "mastercard",
                "paypal", "stripe", "square", "robinhood", "coinbase", "plaid", "chime"],
    "healthcare": ["health", "medical", "pharma", "biotech", "clinical", "care", "wellness",
                   "unitedhealth", "johnson", "pfizer", "cvs", "abbvie", "moderna", "23andme",
                   "oscar", "teladoc", "one medical"],
    "e-commerce": ["shop", "store", "retail", "commerce", "market", "ecommerce", "e-commerce",
                   "shopify", "etsy", "ebay", "wayfair", "instacart", "doordash", "uber", "lyft"],
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

"""
Data Cleaning Module
Handles text normalization, standardization, and data quality improvements
"""
import re
import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and normalize lead data"""
    
    # Company name suffixes to standardize
    COMPANY_SUFFIXES = [
        'Inc.', 'Inc', 'LLC', 'L.L.C.', 'Ltd.', 'Ltd', 'Limited',
        'Corporation', 'Corp.', 'Corp', 'Company', 'Co.', 'Co',
        'LP', 'L.P.', 'LLP', 'L.L.P.', 'PLC', 'P.L.C.'
    ]
    
    # Common job title normalizations
    JOB_TITLE_MAPPINGS = {
        'ceo': 'CEO',
        'cto': 'CTO',
        'cfo': 'CFO',
        'coo': 'COO',
        'cmo': 'CMO',
        'vp': 'VP',
        'svp': 'SVP',
        'evp': 'EVP',
        'c-level': 'C-Level',
        'c level': 'C-Level',
        'v.p.': 'VP',
        'sr.': 'Senior',
        'sr ': 'Senior ',
        'jr.': 'Junior',
        'jr ': 'Junior ',
        'mgr': 'Manager',
        'dir': 'Director',
        'eng': 'Engineer',
        'dev': 'Developer',
    }
    
    # Industry standardization
    INDUSTRY_MAPPINGS = {
        'it': 'Technology',
        'information technology': 'Technology',
        'tech': 'Technology',
        'software': 'Technology',
        'saas': 'Technology',
        'fintech': 'Financial Services',
        'banking': 'Financial Services',
        'finance': 'Financial Services',
        'investment': 'Financial Services',
        'healthcare': 'Healthcare',
        'medical': 'Healthcare',
        'health': 'Healthcare',
        'pharma': 'Healthcare',
        'pharmaceutical': 'Healthcare',
        'ecommerce': 'E-commerce',
        'e-commerce': 'E-commerce',
        'retail': 'E-commerce',
        'online retail': 'E-commerce',
    }
    
    def clean_text(self, text: Any) -> str:
        """
        Clean and normalize text field
        
        Args:
            text: Input text (any type)
            
        Returns:
            Cleaned text string
        """
        if pd.isna(text) or text is None:
            return ''
        
        # Convert to string
        text = str(text).strip()
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing punctuation
        text = text.strip('.,;:!?-_')
        
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable())
        
        return text.strip()
    
    def clean_name(self, name: str) -> str:
        """
        Clean and normalize person name
        
        Args:
            name: Person's name
            
        Returns:
            Cleaned name
        """
        name = self.clean_text(name)
        
        if not name:
            return name
        
        # Remove extra titles
        titles = ['mr.', 'mrs.', 'ms.', 'dr.', 'prof.', 'mr', 'mrs', 'ms', 'dr', 'prof']
        name_lower = name.lower()
        for title in titles:
            if name_lower.startswith(title + ' '):
                name = name[len(title):].strip()
                name_lower = name.lower()
        
        # Capitalize properly (handle multi-word names)
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Handle hyphenated names
        if '-' in name:
            name = '-'.join(word.capitalize() for word in name.split('-'))
        
        return name
    
    def clean_email(self, email: str) -> str:
        """
        Clean and normalize email address
        
        Args:
            email: Email address
            
        Returns:
            Cleaned email (lowercase)
        """
        email = self.clean_text(email)
        
        if not email:
            return email
        
        # Convert to lowercase
        email = email.lower()
        
        # Remove any spaces
        email = email.replace(' ', '')
        
        # Remove common typos
        email = email.replace('@@', '@')
        email = email.replace('..', '.')
        
        return email
    
    def clean_company(self, company: str) -> str:
        """
        Clean and standardize company name
        
        Args:
            company: Company name
            
        Returns:
            Cleaned company name
        """
        company = self.clean_text(company)
        
        if not company:
            return company
        
        # Remove common suffixes for comparison
        # (keep original with suffix for display)
        company_normalized = company
        
        # Standardize common variations
        company = re.sub(r'\b(Incorporated)\b', 'Inc.', company, flags=re.IGNORECASE)
        company = re.sub(r'\b(Corporation)\b', 'Corp.', company, flags=re.IGNORECASE)
        company = re.sub(r'\b(Limited)\b', 'Ltd.', company, flags=re.IGNORECASE)
        company = re.sub(r'\b(Company)\b', 'Co.', company, flags=re.IGNORECASE)
        
        # Remove multiple spaces created by replacements
        company = re.sub(r'\s+', ' ', company).strip()
        
        # Proper capitalization (preserve acronyms)
        words = company.split()
        cleaned_words = []
        for word in words:
            # Keep word as-is if it's an acronym (all caps, 2-5 letters)
            if word.isupper() and 2 <= len(word) <= 5:
                cleaned_words.append(word)
            # Keep suffix as-is if it matches our patterns
            elif any(word == suffix for suffix in self.COMPANY_SUFFIXES):
                cleaned_words.append(word)
            else:
                cleaned_words.append(word.capitalize())
        
        company = ' '.join(cleaned_words)
        
        return company
    
    def clean_job_title(self, job_title: str) -> str:
        """
        Clean and standardize job title
        
        Args:
            job_title: Job title
            
        Returns:
            Cleaned and standardized job title
        """
        job_title = self.clean_text(job_title)
        
        if not job_title:
            return job_title
        
        # Apply mappings (case-insensitive)
        job_title_lower = job_title.lower()
        for key, value in self.JOB_TITLE_MAPPINGS.items():
            # Replace exact matches and matches at word boundaries
            pattern = r'\b' + re.escape(key) + r'\b'
            job_title = re.sub(pattern, value, job_title, flags=re.IGNORECASE)
        
        # Capitalize first letter of each word (preserving acronyms)
        words = job_title.split()
        cleaned_words = []
        for word in words:
            # Keep word as-is if it's a common acronym
            if word.upper() in ['CEO', 'CTO', 'CFO', 'COO', 'CMO', 'VP', 'SVP', 'EVP', 'IT', 'HR', 'PR']:
                cleaned_words.append(word.upper())
            # Keep word if already properly capitalized acronym
            elif word.isupper() and len(word) <= 4:
                cleaned_words.append(word)
            else:
                cleaned_words.append(word.capitalize())
        
        job_title = ' '.join(cleaned_words)
        
        return job_title
    
    def clean_location(self, location: str) -> str:
        """
        Clean and standardize location
        
        Args:
            location: Location string
            
        Returns:
            Cleaned location
        """
        location = self.clean_text(location)
        
        if not location:
            return location
        
        # Standardize state abbreviations
        state_abbrev = {
            'california': 'CA',
            'new york': 'NY',
            'texas': 'TX',
            'florida': 'FL',
            'illinois': 'IL',
            'massachusetts': 'MA',
            # Add more as needed
        }
        
        location_lower = location.lower()
        for state, abbrev in state_abbrev.items():
            if state in location_lower:
                location = location.replace(state, abbrev)
                location = location.replace(state.capitalize(), abbrev)
        
        # Standardize country names
        location = location.replace('U.S.A.', 'USA')
        location = location.replace('U.S.', 'USA')
        location = location.replace('United States', 'USA')
        location = location.replace('U.K.', 'UK')
        location = location.replace('United Kingdom', 'UK')
        
        # Remove extra commas and spaces
        location = re.sub(r'\s*,\s*', ', ', location)
        location = re.sub(r',+', ',', location)
        location = location.strip(',')
        
        return location
    
    def clean_industry(self, industry: Optional[str]) -> Optional[str]:
        """
        Clean and standardize industry
        
        Args:
            industry: Industry string
            
        Returns:
            Cleaned and standardized industry
        """
        if not industry or pd.isna(industry):
            return None
        
        industry = self.clean_text(industry)
        
        if not industry:
            return None
        
        # Apply industry mappings
        industry_lower = industry.lower()
        for key, value in self.INDUSTRY_MAPPINGS.items():
            if key in industry_lower:
                return value
        
        # Capitalize properly if no mapping found
        return industry.title()
    
    def remove_duplicates_by_email(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate rows based on email address
        
        Args:
            df: DataFrame with lead data
            
        Returns:
            DataFrame with duplicates removed
        """
        if 'email' not in df.columns:
            return df
        
        # Keep first occurrence of each email
        original_count = len(df)
        df = df.drop_duplicates(subset=['email'], keep='first')
        removed_count = original_count - len(df)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate email addresses")
        
        return df
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean entire DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Clean each column
        if 'name' in df.columns:
            df['name'] = df['name'].apply(self.clean_name)
        
        if 'email' in df.columns:
            df['email'] = df['email'].apply(self.clean_email)
        
        if 'company' in df.columns:
            df['company'] = df['company'].apply(self.clean_company)
        
        if 'job_title' in df.columns:
            df['job_title'] = df['job_title'].apply(self.clean_job_title)
        
        if 'location' in df.columns:
            df['location'] = df['location'].apply(lambda x: self.clean_location(x) if pd.notna(x) else None)
        
        if 'industry' in df.columns:
            df['industry'] = df['industry'].apply(self.clean_industry)
        
        # Remove duplicates
        df = self.remove_duplicates_by_email(df)
        
        return df


def clean_lead_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main cleaning function for lead data
    
    Args:
        df: DataFrame to clean
        
    Returns:
        Cleaned DataFrame
    """
    cleaner = DataCleaner()
    return cleaner.clean_dataframe(df)

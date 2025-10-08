"""
Process Kaggle LinkedIn Dataset into Lead Format

This script takes the real Kaggle LinkedIn professional profiles dataset
and transforms it into the format expected by our Lead Scoring Dashboard.

Input: LinkedIn people profiles datasets.csv
Output: kaggle_leads.csv with columns: name, email, company, job_title, industry, location
"""

import pandas as pd
import re
import json
from pathlib import Path

def extract_email_from_profile(row):
    """Generate email from name and company"""
    name = str(row.get('name', '')).strip()
    company_name = str(row.get('current_company', '')).strip()
    
    if not name or name == 'null':
        return None
    
    # Clean name - take first and last name
    name_parts = name.split()
    if len(name_parts) >= 2:
        first = name_parts[0].lower()
        last = name_parts[-1].lower()
        # Remove special characters
        first = re.sub(r'[^a-z]', '', first)
        last = re.sub(r'[^a-z]', '', last)
        
        if company_name and company_name != 'null':
            # Extract company domain
            company_clean = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
            email = f"{first}.{last}@{company_clean[:20]}.com"
        else:
            # Use generic email
            domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com']
            email = f"{first}.{last}@{domains[len(name) % len(domains)]}"
        
        return email
    return None

def extract_company_from_experience(row):
    """Extract company name from experience or current_company"""
    # Try current_company first
    if pd.notna(row.get('current_company')):
        try:
            company_data = json.loads(row['current_company'])
            if isinstance(company_data, dict) and company_data.get('name'):
                return company_data['name']
        except:
            # If it's just a string
            company_str = str(row['current_company'])
            if company_str and company_str != 'null':
                return company_str
    
    # Try from experience
    if pd.notna(row.get('experience')):
        try:
            experience = json.loads(row['experience'])
            if isinstance(experience, list) and len(experience) > 0:
                first_exp = experience[0]
                if isinstance(first_exp, dict):
                    return first_exp.get('company', None)
        except:
            pass
    
    return None

def extract_industry_from_experience(row):
    """Extract industry from experience data"""
    if pd.notna(row.get('experience')):
        try:
            experience = json.loads(row['experience'])
            if isinstance(experience, list) and len(experience) > 0:
                first_exp = experience[0]
                if isinstance(first_exp, dict):
                    industry = first_exp.get('industry', None)
                    if industry:
                        # Map to our target industries
                        industry_lower = industry.lower()
                        if any(word in industry_lower for word in ['tech', 'software', 'it', 'computer', 'internet', 'digital']):
                            return 'tech'
                        elif any(word in industry_lower for word in ['finance', 'banking', 'financial', 'investment']):
                            return 'finance'
                        elif any(word in industry_lower for word in ['health', 'medical', 'hospital', 'pharma']):
                            return 'healthcare'
                        elif any(word in industry_lower for word in ['retail', 'ecommerce', 'e-commerce', 'commerce']):
                            return 'e-commerce'
                        else:
                            return industry_lower[:20]  # Keep original if not mapped
        except:
            pass
    return None

def extract_location_from_city(row):
    """Extract location from city and country"""
    city = str(row.get('city', '')).strip()
    country = str(row.get('country_code', '')).strip()
    
    if city and city != 'null':
        # Clean city name
        city_clean = city.split(',')[0].strip()
        return city_clean
    elif country and country != 'null':
        return country
    return None

def process_kaggle_dataset():
    """Main processing function"""
    print("🚀 Processing Kaggle LinkedIn Dataset...")
    
    # Paths
    input_file = Path("/home/jainam/Projects/AI-Lead-Scoring-and-Enrichment-Dashboard/kaggle-datasets/LinkedIn Professional Profiles Dataset/LinkedIn people profiles datasets.csv")
    output_file = Path("/home/jainam/Projects/AI-Lead-Scoring-and-Enrichment-Dashboard/backend/kaggle_leads.csv")
    
    # Read dataset
    print(f"📖 Reading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"✅ Found {len(df)} profiles in dataset")
    
    # Create leads list
    leads = []
    errors = 0
    
    print("🔄 Processing profiles...")
    for idx, row in df.iterrows():
        try:
            # Extract data
            name = str(row.get('name', '')).strip()
            if not name or name == 'null' or len(name) < 3:
                errors += 1
                continue
            
            # Extract job title from position
            job_title = str(row.get('position', '')).strip()
            if not job_title or job_title == 'null':
                errors += 1
                continue
            
            # Extract company
            company = extract_company_from_experience(row)
            if not company or company == 'null':
                errors += 1
                continue
            
            # Generate email
            email = extract_email_from_profile(row)
            if not email:
                errors += 1
                continue
            
            # Extract location
            location = extract_location_from_city(row)
            
            # Extract industry
            industry = extract_industry_from_experience(row)
            
            # Create lead
            lead = {
                'name': name[:100],  # Limit length
                'email': email[:100],
                'company': company[:100],
                'job_title': job_title[:150],
                'industry': industry if industry else '',
                'location': location if location else ''
            }
            
            leads.append(lead)
            
            # Progress indicator
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(df)} profiles ({len(leads)} valid leads, {errors} errors)")
        
        except Exception as e:
            errors += 1
            continue
    
    # Create DataFrame
    leads_df = pd.DataFrame(leads)
    
    # Save to CSV
    print(f"\n💾 Saving to {output_file}...")
    leads_df.to_csv(output_file, index=False)
    
    # Statistics
    print("\n" + "="*60)
    print("📊 Processing Statistics:")
    print("="*60)
    print(f"Total profiles in dataset: {len(df)}")
    print(f"Valid leads created: {len(leads)}")
    print(f"Errors/skipped: {errors}")
    print(f"Success rate: {len(leads)/len(df)*100:.1f}%")
    print(f"\nOutput file: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024:.1f} KB")
    
    # Industry breakdown
    if len(leads_df) > 0:
        print("\n📈 Industry Distribution:")
        industry_counts = leads_df['industry'].value_counts()
        for industry, count in industry_counts.head(10).items():
            print(f"  {industry or '(none)'}: {count} ({count/len(leads_df)*100:.1f}%)")
        
        # Location breakdown
        print("\n🌍 Top 10 Locations:")
        location_counts = leads_df['location'].value_counts()
        for location, count in location_counts.head(10).items():
            print(f"  {location or '(none)'}: {count} ({count/len(leads_df)*100:.1f}%)")
    
    print("\n✅ Processing complete!")
    print(f"📁 You can now upload {output_file} to the dashboard")

if __name__ == "__main__":
    process_kaggle_dataset()

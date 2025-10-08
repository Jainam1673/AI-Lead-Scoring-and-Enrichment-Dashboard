# Dataset Information

## Overview

The `sample-leads.csv` file contains **200 realistic B2B contact leads** generated for demonstration purposes.

## Dataset Composition

### Companies (78 unique)
The dataset includes contacts from major companies across multiple sectors:

#### Technology (48 companies)
- **Large Tech (5000+)**: Google, Microsoft, Amazon, Apple, Meta, Netflix, Salesforce, Oracle, IBM, Adobe
- **Mid-size SaaS (1000-5000)**: Stripe, Databricks, Snowflake, MongoDB, HashiCorp, Datadog, Twilio, Zoom, Dropbox, DocuSign, HubSpot, Zendesk, Slack, Asana, GitLab
- **Growing Startups (200-1000)**: Notion, Figma, Vercel, Anthropic, Scale AI, Hugging Face, Weights & Biases
- **Early Stage (50-200)**: Linear, Supabase, Replicate

#### Finance (15 companies)
- **Banking (5000+)**: Goldman Sachs, Morgan Stanley, JPMorgan Chase, Citigroup, Bank of America, Wells Fargo
- **Payments (5000+)**: American Express, Visa, Mastercard, PayPal
- **FinTech (1000-5000)**: Square, Robinhood, Coinbase
- **FinTech (200-1000)**: Plaid, Chime

#### Healthcare (10 companies)
- **Healthcare (5000+)**: UnitedHealth, Johnson & Johnson, Pfizer, CVS Health, AbbVie
- **BioTech (1000-5000)**: Moderna
- **HealthTech (200-1000 to 1000-5000)**: 23andMe, Oscar Health, Teladoc, One Medical

#### E-commerce/Mobility (8 companies)
- **E-commerce (5000+)**: Shopify, eBay, Wayfair, Uber
- **E-commerce (1000-5000)**: Etsy, Instacart, DoorDash, Lyft

### Job Titles (51 unique)
The dataset includes realistic job titles across all seniority levels:
- **C-Level**: CEO, CTO, CFO, COO, CMO, Chief Data Officer, Chief Revenue Officer
- **VP Level**: VP of Sales, VP of Engineering, VP of Marketing, VP of Product, VP of Operations
- **Director Level**: Director of Sales, Director of Engineering, Director of Marketing, Director of Product, Director of Business Development, Director of Customer Success
- **Manager Level**: Sales Manager, Engineering Manager, Marketing Manager, Product Manager, Account Manager, Customer Success Manager, Business Development Manager
- **Individual Contributors**: Senior Sales Executive, Lead Software Engineer, Senior Product Designer, Marketing Specialist, Account Executive, Business Analyst, Data Scientist

### Contact Names
200 realistic names combining:
- 80 common first names (diverse, representing various backgrounds)
- 80 common last names (diverse ethnic representation)

### Email Addresses
Realistic email patterns:
- **Company emails** (70%): `first.last@company.com`, `flast@company.com`, `firstl@company.com`
- **Personal emails** (30%): Gmail, Yahoo, Outlook, iCloud, ProtonMail, Hotmail domains

### Locations (20+ cities)
Major business hubs including:
- **West Coast**: San Francisco, Mountain View, Cupertino, San Jose, Los Gatos, Seattle, Menlo Park
- **East Coast**: New York, Boston, Cambridge, Charlotte, Woonsocket, New Brunswick, Armonk
- **Central**: Chicago, Austin, Minneapolis
- **International**: Ottawa (Canada), Sydney (Australia), Tel Aviv (Israel)

## Data Generation Method

The dataset was generated using:
1. **Real company profiles**: Accurate company names, industries, and approximate sizes based on 2024-2025 public data
2. **Realistic job hierarchy**: Authentic job titles reflecting actual business structures
3. **Common names**: Statistically common first and last names to simulate real contact databases
4. **Email patterns**: Industry-standard email formats (company domains and personal email providers)
5. **Geographic distribution**: Concentration in major tech/finance hubs matching actual business demographics

## Purpose

This dataset serves as **demonstration data** for the AI Lead Scoring & Enrichment Dashboard to:
- Showcase the scoring algorithm with realistic business scenarios
- Demonstrate enrichment capabilities across various company sizes and industries
- Provide meaningful filter and sort testing data
- Enable realistic CSV import/export workflows

## Data Privacy

- ❌ No real individuals are represented in this dataset
- ❌ No actual email addresses are used (all are fictional)
- ❌ No personal or confidential information is included
- ✅ All data is synthetic and generated for demonstration purposes only

## Statistics

- **Total Records**: 200 leads
- **Average Score**: 87.7/100
- **High-Quality Leads** (≥70): 187 (93.5%)
- **Valid Emails**: ~85% (realistic validation rate)
- **Target Industries**: 80% of leads (Tech, Finance, Healthcare)
- **Decision-Makers** (C-Level/VP/Director): ~60% of leads

## Usage

This dataset is included for:
- Initial demo when the dashboard is first loaded
- Testing the scoring algorithm with diverse scenarios
- Showcasing the enrichment logic across company types
- Providing sample data for CSV upload testing

Users can replace this with their own lead data by uploading any CSV with the columns:
- `name` (required)
- `email` (required)
- `company` (required)
- `job_title` (required)
- `industry` (optional - will be auto-enriched)
- `location` (optional)

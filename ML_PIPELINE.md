# ML Processing Pipeline Documentation

## Overview

The AI Lead Scoring Dashboard uses a **comprehensive 6-stage ML processing pipeline** to transform raw CSV data into enriched, scored, and prioritized leads. The pipeline ensures data quality, handles errors gracefully, and provides real-time progress feedback to users.

## Pipeline Architecture

```
Raw CSV Upload
    ↓
┌─────────────────────────────────────────┐
│  Stage 1: Data Validation               │
│  - File format & encoding checks        │
│  - Required field validation            │
│  - Email format validation              │
│  - Duplicate detection                  │
│  - Data quality assessment              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Stage 2: Data Cleaning                 │
│  - Text normalization                   │
│  - Whitespace removal                   │
│  - Company name standardization         │
│  - Job title normalization              │
│  - Location parsing                     │
│  - Duplicate removal                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Stage 3: Feature Extraction            │
│  - Convert DataFrame to Lead objects    │
│  - Extract structured fields            │
│  - Handle missing data                  │
│  - Type conversion & validation         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Stage 4: Data Enrichment               │
│  - Company size classification          │
│  - Industry categorization              │
│  - LinkedIn URL generation              │
│  - Email validation                     │
│  - Fallback strategies for API failures │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Stage 5: Lead Scoring                  │
│  - Rule-based ML scoring (0-100)        │
│  - Job title scoring (0-10 points)      │
│  - Company size scoring (0-10 points)   │
│  - Industry match scoring (0-10 points) │
│  - Email validation (-10 to +5 points)  │
│  - Score normalization                  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Stage 6: Quality Check                 │
│  - Final data validation                │
│  - Quality metrics generation           │
│  - Score distribution analysis          │
│  - Success rate calculation             │
└─────────────────────────────────────────┘
    ↓
Enriched & Scored Leads
```

## Stage Details

### Stage 1: Data Validation

**Module**: `backend/src/utils/validation.py`

**Purpose**: Ensure uploaded data meets minimum quality standards before processing.

**Checks Performed**:
- ✅ File format validation (CSV only)
- ✅ File size limits (max 50MB)
- ✅ Encoding detection (UTF-8, Latin-1)
- ✅ Required columns present (`name`, `email`, `company`, `job_title`)
- ✅ Empty file detection
- ✅ Duplicate email detection
- ✅ Email format validation (RFC 5322 compliant)
- ✅ Field length validation
- ✅ Data type validation
- ✅ Placeholder data detection
- ✅ Personal email detection (Gmail, Yahoo, etc.)

**Error Handling**:
- Returns detailed error messages for missing columns
- Provides warnings for data quality issues
- Calculates validation statistics (success rate, error counts)
- Continues processing if at least 50% of rows are valid

**Output**:
```python
ValidationResult(
    is_valid=True,
    errors=[],
    warnings=["Found 5 duplicate emails", "20% using personal emails"],
    stats={
        'total_rows': 1000,
        'valid_rows': 950,
        'invalid_rows': 50,
        'duplicate_emails': 5,
        'invalid_emails': 15
    }
)
```

### Stage 2: Data Cleaning

**Module**: `backend/src/utils/cleaning.py`

**Purpose**: Normalize and standardize data for consistent processing.

**Operations**:
1. **Text Normalization**
   - Remove leading/trailing whitespace
   - Remove multiple consecutive spaces
   - Remove control characters
   - Strip leading/trailing punctuation

2. **Name Cleaning**
   - Remove titles (Mr., Mrs., Dr., etc.)
   - Proper capitalization (Title Case)
   - Handle hyphenated names
   - Preserve multi-word names

3. **Email Cleaning**
   - Convert to lowercase
   - Remove spaces
   - Fix common typos (`@@` → `@`, `..` → `.`)

4. **Company Standardization**
   - Standardize suffixes (Incorporated → Inc., Corporation → Corp.)
   - Proper capitalization (preserve acronyms)
   - Remove redundant spaces

5. **Job Title Normalization**
   - Map abbreviations (CEO, CTO, VP, SVP, etc.)
   - Expand common abbreviations (Sr. → Senior, Jr. → Junior)
   - Proper capitalization (preserve acronyms)

6. **Location Parsing**
   - Standardize state abbreviations (California → CA)
   - Standardize country names (United States → USA)
   - Remove extra commas

7. **Industry Standardization**
   - Map to standard categories (tech, finance, healthcare, e-commerce)
   - Handle common variations (IT → Technology, Fintech → Financial Services)

8. **Duplicate Removal**
   - Remove duplicate emails (keep first occurrence)
   - Log duplicate count

**Output**: Cleaned DataFrame with standardized, normalized data

### Stage 3: Feature Extraction

**Module**: `backend/src/routes/api.py` (feature_extraction_stage function)

**Purpose**: Convert cleaned DataFrame to structured Lead objects for enrichment.

**Operations**:
- Parse each row into `Lead` Pydantic model
- Handle missing optional fields (location, industry, company_size)
- Validate required fields are present
- Generate sequential lead IDs
- Catch and log parsing errors

**Error Handling**:
- Skip rows with parsing errors
- Log detailed error messages (row number, error description)
- Continue processing valid rows
- Return at least partial results if some rows succeed

**Output**: List of `Lead` objects ready for enrichment

### Stage 4: Data Enrichment

**Module**: `backend/src/utils/enrichment.py`

**Purpose**: Add valuable context and metadata to each lead.

**Enrichment Operations**:
1. **Company Size Classification**
   - Lookup company in size database (5000+ companies)
   - Classify as: `5000+`, `1000-5000`, `200-1000`, `50-200`, `<50`
   - Fallback to `unknown` if not found

2. **Industry Categorization**
   - Auto-classify based on company name patterns
   - Categories: Technology, Financial Services, Healthcare, E-commerce
   - Fallback to existing industry or `unspecified`

3. **LinkedIn URL Generation**
   - Generate LinkedIn profile search URL
   - Format: `https://linkedin.com/in/{normalized-name}`
   - Normalize name (lowercase, replace spaces with hyphens)

4. **Email Validation**
   - Basic format validation (already done in Stage 1)
   - Set `email_valid` flag

**Error Handling**:
- Continue with partial enrichment if some operations fail
- Use fallback values for missing data
- Log warnings for enrichment failures
- Never fail entire pipeline due to enrichment issues

**Output**: List of enriched `Lead` objects with additional metadata

### Stage 5: Lead Scoring

**Module**: `backend/src/utils/scoring.py`

**Purpose**: Assign 0-100 score to each lead based on multiple factors.

**Scoring Formula**:
```
Raw Score = JobTitleScore + CompanySizeScore + IndustryScore + EmailScore
Normalized Score = ((Raw Score + 10) / 45) × 100
```

**Scoring Criteria**:

| Factor | Points | Logic |
|--------|--------|-------|
| **Job Title** | 0-10 | CEO/C-Suite (10), VP/Director (7), Manager (5), Other (2-3) |
| **Company Size** | 0-10 | 5000+ (10), 1000-5000 (9), 200-1000 (7), 50-200 (5), <50 (3) |
| **Industry Match** | 0-10 | Target industries (tech/finance/healthcare) (10), Other (0) |
| **Email Validation** | -10 to +5 | Valid email (+5), Invalid email (-10) |

**Score Interpretation**:
- **70-100**: High-priority leads (decision-makers at target companies)
- **40-69**: Medium-priority leads (worth reviewing)
- **0-39**: Low-priority leads (may not be a good fit)

**Output**: List of `ScoredLead` objects with scores and breakdowns

### Stage 6: Quality Check

**Module**: `backend/src/routes/api.py` (quality_check_stage function)

**Purpose**: Final validation and quality metrics generation.

**Quality Checks**:
- Verify all leads have valid emails
- Verify all leads have scores
- Remove any invalid leads
- Calculate final statistics

**Quality Metrics Generated**:
```json
{
  "timestamp": "2025-10-08T12:34:56",
  "total_records": 1000,
  "processed_records": 980,
  "successful_records": 950,
  "failed_records": 50,
  "success_rate": 95.0,
  "total_warnings": 12,
  "total_errors": 3,
  "stage_summary": [
    {
      "stage": "validation",
      "status": "completed",
      "duration": 0.45,
      "records_processed": 1000,
      "success_rate": 98.0
    },
    // ... other stages
  ],
  "quality_metrics": {
    "average_score": 72.3,
    "high_quality_leads": 720,
    "high_quality_percentage": 72.0
  }
}
```

**Output**: Final list of validated `ScoredLead` objects + quality report

## Error Handling Strategy

### File Upload Errors

| Error | HTTP Code | User Message |
|-------|-----------|-------------|
| Wrong file type | 400 | "Only CSV files are allowed. Please upload a file with .csv extension." |
| File too large | 413 | "File too large (X MB). Maximum size is 50MB. Please split your file or contact support." |
| Empty file | 400 | "CSV file is empty. Please upload a file with lead data." |
| Encoding issues | 400 | "Unable to decode CSV file. Please ensure it's properly encoded (UTF-8 or Latin-1)." |
| Too many leads | 413 | "Too many leads (X). Maximum is 50,000 per upload. Please split your file into smaller batches." |

### Validation Errors

| Error | Handling |
|-------|----------|
| Missing columns | Return 400 with specific columns needed |
| Empty columns | Return 400 with list of empty required columns |
| Invalid email formats | Continue processing, flag as warning |
| Duplicate emails | Continue processing, remove duplicates, log warning |
| Low success rate (<50%) | Return 400 with error details |

### Processing Errors

| Error | Handling |
|-------|----------|
| Parsing error (individual row) | Skip row, log warning, continue processing |
| Enrichment API failure | Use fallback values, log warning, continue |
| Scoring error | Use default score, log error, continue |
| Quality check failure | Return partial results with warnings |

### Recovery Mechanisms

1. **Partial Success Handling**
   - Process as many rows as possible
   - Return successful rows even if some fail
   - Provide detailed error report

2. **Fallback Strategies**
   - Use default values when enrichment fails
   - Continue with available data if optional fields missing
   - Downgrade errors to warnings when possible

3. **User-Friendly Messaging**
   - Clear, actionable error messages
   - Specific guidance on fixing issues
   - Links to documentation or support

## Progress Tracking

### Backend Progress API

**Endpoint**: `GET /api/processing-progress`

**Response**:
```json
{
  "status": "processing",
  "current_stage": "enrichment",
  "current_stage_status": "running",
  "progress_percentage": 57,
  "total_records": 1000,
  "processed_records": 572,
  "successful_records": 560,
  "failed_records": 12,
  "warnings_count": 5,
  "errors_count": 2,
  "stage_results": [
    {
      "stage": "validation",
      "status": "completed",
      "duration": 0.45,
      "records_processed": 1000
    },
    // ... other completed stages
  ]
}
```

### Frontend Progress Component

**Component**: `ProcessingProgress.tsx`

**Features**:
- Real-time progress bar (0-100%)
- Stage-by-stage visualization with icons
- Success/failure indicators
- Statistics dashboard (total, successful, failed, warnings)
- Warning/error messages
- Animated transitions

**Usage**:
```tsx
<ProcessingProgress
  currentStage="enrichment"
  currentStageStatus="running"
  progressPercentage={57}
  totalRecords={1000}
  processedRecords={572}
  successfulRecords={560}
  failedRecords={12}
  warningsCount={5}
  errorsCount={2}
  stageResults={[...]}
/>
```

## Testing Edge Cases

### Test Scenarios

1. **Malformed CSV**
   - Missing quotes
   - Inconsistent column counts
   - Mixed line endings (CRLF vs LF)

2. **Missing Columns**
   - Missing required columns
   - Misspelled column names
   - Extra unexpected columns

3. **Invalid Data**
   - Invalid email formats
   - Empty required fields
   - Null values in required fields

4. **Special Characters**
   - Unicode characters (emojis, accents)
   - HTML entities
   - Escape characters

5. **Large Files**
   - 10,000 rows (tested)
   - 50,000 rows (max limit)
   - 100MB+ files (should reject)

6. **Duplicate Data**
   - Exact duplicate rows
   - Duplicate emails only
   - Similar names/companies

7. **Encoding Issues**
   - UTF-8 with BOM
   - Latin-1 encoding
   - Mixed encodings

## Performance Metrics

### Current Benchmarks

| Dataset Size | Processing Time | Throughput |
|--------------|----------------|------------|
| 200 leads | 0.15s | 1,333 leads/sec |
| 889 leads | 0.60s | 1,481 leads/sec |
| 10,000 leads | 1.24s | 8,064 leads/sec |
| 50,000 leads | ~6s (est) | 8,333 leads/sec |

### Optimization Strategies

1. **Batch Processing** (future enhancement)
   - Process leads in batches of 1,000
   - Parallel processing for enrichment
   - Async API calls

2. **Caching** (future enhancement)
   - Cache company size lookups
   - Cache industry classifications
   - Redis for distributed caching

3. **Database Optimization** (future enhancement)
   - Bulk inserts instead of individual
   - Indexed queries
   - Connection pooling

## API Response Format

### Success Response

```json
{
  "leads": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@techcorp.com",
      "company": "TechCorp Inc.",
      "job_title": "CEO",
      "industry": "Technology",
      "location": "San Francisco, CA",
      "company_size": "1000-5000",
      "linkedin_url": "https://linkedin.com/in/john-doe",
      "email_valid": true,
      "score": 92.2,
      "score_breakdown": {
        "job_title_score": 10,
        "company_size_score": 9,
        "industry_score": 10,
        "email_score": 5
      }
    },
    // ... more leads
  ],
  "quality_report": {
    "timestamp": "2025-10-08T12:34:56",
    "total_records": 1000,
    "successful_records": 950,
    "success_rate": 95.0,
    // ... more metrics
  },
  "processing_time": 1.24,
  "success_rate": 95.0
}
```

### Error Response

```json
{
  "detail": "Processing pipeline failed: Data validation failed:\nMissing required columns: email, company\nRequired columns are: name, email, company, job_title"
}
```

## Future Enhancements

1. **Machine Learning Models**
   - Train on historical conversion data
   - Predictive lead scoring
   - Automated feature engineering

2. **Real-time APIs**
   - Clearbit integration for company data
   - Hunter.io for email verification
   - LinkedIn API for profile enrichment

3. **Advanced Analytics**
   - Score distribution visualization
   - A/B testing different scoring algorithms
   - Lead quality trends over time

4. **Scalability**
   - Celery task queue for async processing
   - Redis caching layer
   - PostgreSQL for data persistence

5. **Monitoring**
   - Pipeline performance metrics
   - Error rate tracking
   - Data quality dashboards

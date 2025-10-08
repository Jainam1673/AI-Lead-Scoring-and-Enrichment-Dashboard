"""
Data Validation Module
Handles all data validation, format checking, and data quality assessment
"""
import re
import pandas as pd
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    stats: Dict[str, Any]
    
@dataclass
class RowValidationResult:
    """Result of individual row validation"""
    row_index: int
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    cleaned_data: Dict[str, Any] | None


class DataValidator:
    """Comprehensive data validation for lead data"""
    
    # Email regex pattern (RFC 5322 simplified)
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Required columns for lead data
    REQUIRED_COLUMNS = ['name', 'email', 'company', 'job_title']
    
    # Optional columns
    OPTIONAL_COLUMNS = ['location', 'industry', 'company_size', 'phone']
    
    # Max lengths for text fields
    MAX_LENGTHS = {
        'name': 100,
        'email': 150,
        'company': 200,
        'job_title': 150,
        'location': 200,
        'industry': 100,
    }
    
    def __init__(self):
        self.validation_stats = {
            'total_rows': 0,
            'valid_rows': 0,
            'invalid_rows': 0,
            'rows_with_warnings': 0,
            'duplicate_emails': 0,
            'invalid_emails': 0,
            'missing_required_fields': 0,
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> ValidationResult:
        """
        Validate entire DataFrame structure and content
        
        Args:
            df: Input DataFrame with lead data
            
        Returns:
            ValidationResult with validation status and details
        """
        errors = []
        warnings = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append("CSV file is empty - no data rows found")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                stats=self.validation_stats
            )
        
        self.validation_stats['total_rows'] = len(df)
        
        # Check for required columns
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            errors.append(f"Required columns are: {', '.join(self.REQUIRED_COLUMNS)}")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                stats=self.validation_stats
            )
        
        # Check for completely empty columns
        for col in self.REQUIRED_COLUMNS:
            if df[col].isna().all():
                errors.append(f"Required column '{col}' is completely empty")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                stats=self.validation_stats
            )
        
        # Check for duplicate emails
        duplicate_emails = df[df['email'].notna()]['email'].duplicated().sum()
        if duplicate_emails > 0:
            self.validation_stats['duplicate_emails'] = duplicate_emails
            warnings.append(f"Found {duplicate_emails} duplicate email addresses - only first occurrence will be kept")
        
        # Check data types and format issues
        self._check_data_quality(df, warnings)
        
        # Validate individual rows
        row_results = []
        for idx, row in df.iterrows():
            result = self.validate_row(idx, row)
            row_results.append(result)
            
            if not result.is_valid:
                self.validation_stats['invalid_rows'] += 1
            else:
                self.validation_stats['valid_rows'] += 1
                
            if result.warnings:
                self.validation_stats['rows_with_warnings'] += 1
        
        # Calculate success rate
        success_rate = (self.validation_stats['valid_rows'] / self.validation_stats['total_rows']) * 100
        
        if success_rate < 50:
            warnings.append(f"Low data quality: only {success_rate:.1f}% of rows are valid")
        
        # At least some valid rows needed
        if self.validation_stats['valid_rows'] == 0:
            errors.append("No valid rows found in CSV file")
            errors.append("Common issues: invalid email formats, missing required fields, malformed data")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                stats=self.validation_stats
            )
        
        return ValidationResult(
            is_valid=True,
            errors=errors,
            warnings=warnings,
            stats=self.validation_stats
        )
    
    def validate_row(self, idx: int, row: pd.Series) -> RowValidationResult:
        """
        Validate individual row data
        
        Args:
            idx: Row index
            row: Pandas Series representing the row
            
        Returns:
            RowValidationResult with validation status
        """
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Check required fields
        for field in self.REQUIRED_COLUMNS:
            value = row.get(field)
            
            # Check if field is missing or empty
            if pd.isna(value) or str(value).strip() == '':
                errors.append(f"Missing required field: {field}")
                self.validation_stats['missing_required_fields'] += 1
                continue
            
            # Convert to string and strip whitespace
            cleaned_value = str(value).strip()
            
            # Check max length
            if field in self.MAX_LENGTHS:
                max_len = self.MAX_LENGTHS[field]
                if len(cleaned_value) > max_len:
                    warnings.append(f"Field '{field}' exceeds max length ({max_len}), will be truncated")
                    cleaned_value = cleaned_value[:max_len]
            
            # Special validation for email
            if field == 'email':
                email_valid, email_error = self.validate_email(cleaned_value)
                if not email_valid:
                    errors.append(f"Invalid email format: {email_error}")
                    self.validation_stats['invalid_emails'] += 1
                else:
                    cleaned_value = cleaned_value.lower()  # Normalize email to lowercase
            
            # Special validation for name
            if field == 'name':
                if len(cleaned_value) < 2:
                    errors.append(f"Name is too short: '{cleaned_value}'")
                elif not any(c.isalpha() for c in cleaned_value):
                    errors.append(f"Name contains no letters: '{cleaned_value}'")
            
            cleaned_data[field] = cleaned_value
        
        # If required fields failed, row is invalid
        if errors:
            return RowValidationResult(
                row_index=idx,
                is_valid=False,
                errors=errors,
                warnings=warnings,
                cleaned_data=None
            )
        
        # Process optional fields
        for field in self.OPTIONAL_COLUMNS:
            if field in row:
                value = row.get(field)
                if pd.notna(value) and str(value).strip() != '':
                    cleaned_value = str(value).strip()
                    
                    # Check max length
                    if field in self.MAX_LENGTHS:
                        max_len = self.MAX_LENGTHS[field]
                        if len(cleaned_value) > max_len:
                            cleaned_value = cleaned_value[:max_len]
                    
                    cleaned_data[field] = cleaned_value
                else:
                    cleaned_data[field] = None
        
        return RowValidationResult(
            row_index=idx,
            is_valid=True,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data
        )
    
    def validate_email(self, email: str) -> Tuple[bool, str | None]:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or not isinstance(email, str):
            return False, "Email is empty or not a string"
        
        email = email.strip()
        
        if len(email) < 5:  # Minimum: a@b.c
            return False, "Email is too short"
        
        if len(email) > 150:
            return False, "Email is too long"
        
        if not self.EMAIL_PATTERN.match(email):
            return False, "Email format is invalid"
        
        # Additional checks
        if email.count('@') != 1:
            return False, "Email must contain exactly one @ symbol"
        
        local, domain = email.split('@')
        
        if not local or not domain:
            return False, "Email local or domain part is empty"
        
        if '.' not in domain:
            return False, "Email domain must contain at least one dot"
        
        # Check for common typos
        common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        typo_domains = ['gmial.com', 'gmai.com', 'yahooo.com', 'outlok.com']
        
        for typo in typo_domains:
            if domain.lower() == typo:
                return False, f"Possible typo in email domain: {domain}"
        
        return True, None
    
    def _check_data_quality(self, df: pd.DataFrame, warnings: List[str]):
        """Check overall data quality and add warnings"""
        
        # Check for high percentage of missing optional fields
        for col in self.OPTIONAL_COLUMNS:
            if col in df.columns:
                missing_pct = (df[col].isna().sum() / len(df)) * 100
                if missing_pct > 80:
                    warnings.append(f"Column '{col}' is {missing_pct:.0f}% empty - this may affect enrichment quality")
        
        # Check for suspicious patterns
        if 'email' in df.columns:
            # Check for high percentage of personal emails
            personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
            personal_email_count = 0
            
            for email in df['email'].dropna():
                email_str = str(email).lower()
                if any(domain in email_str for domain in personal_domains):
                    personal_email_count += 1
            
            if personal_email_count > 0:
                personal_pct = (personal_email_count / len(df)) * 100
                if personal_pct > 50:
                    warnings.append(f"{personal_pct:.0f}% of emails are personal (Gmail, Yahoo, etc.) - business emails are preferred for B2B leads")
        
        # Check for placeholder data
        placeholder_patterns = ['test', 'example', 'sample', 'dummy', 'lorem ipsum', 'asdf', 'xxx']
        placeholder_count = 0
        
        for col in self.REQUIRED_COLUMNS:
            if col in df.columns:
                for value in df[col].dropna():
                    value_str = str(value).lower()
                    if any(pattern in value_str for pattern in placeholder_patterns):
                        placeholder_count += 1
                        break
        
        if placeholder_count > len(df) * 0.1:
            warnings.append("Detected placeholder/test data in CSV - this may affect results")


def validate_csv_file(df: pd.DataFrame) -> ValidationResult:
    """
    Main validation function for CSV data
    
    Args:
        df: DataFrame to validate
        
    Returns:
        ValidationResult object
    """
    validator = DataValidator()
    return validator.validate_dataframe(df)

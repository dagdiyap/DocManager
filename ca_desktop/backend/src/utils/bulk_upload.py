"""Bulk client upload utilities for parsing Excel and text files."""

import re
from typing import List, Dict, Optional, Tuple
import pandas as pd
from io import BytesIO
from shared.utils.logging import get_logger

logger = get_logger(__name__)


def extract_phone_number(text: str) -> Optional[str]:
    """
    Extract 10-digit Indian phone number from text.
    Handles formats: +91XXXXXXXXXX, 91XXXXXXXXXX, XXXXXXXXXX
    
    Args:
        text: Text containing phone number
        
    Returns:
        10-digit phone number or None if not found
    """
    if not text:
        return None
    
    # Convert to string and remove whitespace
    text = str(text).strip().replace(" ", "").replace("-", "")
    
    # Pattern 1: +91 followed by 10 digits
    match = re.search(r'\+91(\d{10})', text)
    if match:
        return match.group(1)
    
    # Pattern 2: 91 followed by 10 digits (without +)
    match = re.search(r'(?<!\d)91(\d{10})(?!\d)', text)
    if match:
        return match.group(1)
    
    # Pattern 3: 10 digits starting with 6-9 (valid Indian mobile)
    match = re.search(r'(?<!\d)([6-9]\d{9})(?!\d)', text)
    if match:
        return match.group(1)
    
    return None


def find_phone_column(df: pd.DataFrame) -> Optional[str]:
    """
    Automatically detect the phone number column in a DataFrame.
    
    Args:
        df: DataFrame to search
        
    Returns:
        Column name containing phone numbers or None
    """
    # First, check column names for common phone-related keywords
    phone_keywords = ['phone', 'mobile', 'contact', 'number', 'cell', 'tel']
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in phone_keywords):
            # Verify this column actually contains phone numbers
            sample = df[col].dropna().head(5)
            if any(extract_phone_number(str(val)) for val in sample):
                logger.info(f"Found phone column by name: {col}")
                return col
    
    # If not found by name, check each column's content
    for col in df.columns:
        sample = df[col].dropna().head(10)
        phone_count = sum(1 for val in sample if extract_phone_number(str(val)))
        if phone_count >= len(sample) * 0.7:  # 70% of samples are phone numbers
            logger.info(f"Found phone column by content: {col}")
            return col
    
    return None


def parse_excel_file(file_content: bytes) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Parse Excel file and extract client data.
    
    Args:
        file_content: Excel file content as bytes
        
    Returns:
        Tuple of (valid_clients, errors)
        valid_clients: List of dicts with phone_number, name, email
        errors: List of error messages
    """
    clients = []
    errors = []
    
    try:
        # Read Excel file
        df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
        
        if df.empty:
            errors.append("Excel file is empty")
            return clients, errors
        
        # Find phone number column
        phone_col = find_phone_column(df)
        if not phone_col:
            errors.append("Could not find phone number column. Please ensure one column contains 10-digit Indian phone numbers.")
            return clients, errors
        
        # Find name column (common keywords)
        name_col = None
        name_keywords = ['name', 'client', 'customer', 'person']
        for col in df.columns:
            if any(keyword in str(col).lower() for keyword in name_keywords):
                name_col = col
                break
        
        # Find email column
        email_col = None
        email_keywords = ['email', 'mail', 'e-mail']
        for col in df.columns:
            if any(keyword in str(col).lower() for keyword in email_keywords):
                email_col = col
                break
        
        logger.info(f"Detected columns - Phone: {phone_col}, Name: {name_col}, Email: {email_col}")
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Extract phone number
                phone_raw = row[phone_col]
                phone = extract_phone_number(str(phone_raw))
                
                if not phone:
                    errors.append(f"Row {idx + 2}: Invalid phone number '{phone_raw}'")
                    continue
                
                # Extract name (use phone as fallback)
                name = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else f"Client {phone}"
                
                # Extract email (optional)
                email = str(row[email_col]).strip() if email_col and pd.notna(row[email_col]) else None
                if email and '@' not in email:
                    email = None  # Invalid email
                
                clients.append({
                    "phone_number": phone,
                    "name": name,
                    "email": email,
                })
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        logger.info(f"Parsed {len(clients)} valid clients from Excel, {len(errors)} errors")
        
    except Exception as e:
        errors.append(f"Failed to parse Excel file: {str(e)}")
    
    return clients, errors


def parse_text_file(file_content: bytes) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Parse text file and extract client data.
    Expects format: phone_number, name, email (one per line)
    Or just phone numbers (one per line)
    
    Args:
        file_content: Text file content as bytes
        
    Returns:
        Tuple of (valid_clients, errors)
    """
    clients = []
    errors = []
    
    try:
        # Decode text file
        text = file_content.decode('utf-8')
        lines = text.strip().split('\n')
        
        for idx, line in enumerate(lines, start=1):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            
            try:
                # Try comma-separated format first
                if ',' in line:
                    parts = [p.strip() for p in line.split(',')]
                    phone = extract_phone_number(parts[0])
                    name = parts[1] if len(parts) > 1 else None
                    email = parts[2] if len(parts) > 2 else None
                else:
                    # Just phone number
                    phone = extract_phone_number(line)
                    name = None
                    email = None
                
                if not phone:
                    errors.append(f"Line {idx}: Could not extract valid phone number from '{line}'")
                    continue
                
                # Use phone as name if name not provided
                if not name:
                    name = f"Client {phone}"
                
                # Validate email
                if email and '@' not in email:
                    email = None
                
                clients.append({
                    "phone_number": phone,
                    "name": name,
                    "email": email,
                })
                
            except Exception as e:
                errors.append(f"Line {idx}: {str(e)}")
        
        logger.info(f"Parsed {len(clients)} valid clients from text file, {len(errors)} errors")
        
    except Exception as e:
        errors.append(f"Failed to parse text file: {str(e)}")
    
    return clients, errors


def deduplicate_clients(clients: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], int]:
    """
    Remove duplicate phone numbers, keeping the first occurrence.
    
    Args:
        clients: List of client dicts
        
    Returns:
        Tuple of (unique_clients, duplicate_count)
    """
    seen_phones = set()
    unique_clients = []
    
    for client in clients:
        phone = client["phone_number"]
        if phone not in seen_phones:
            seen_phones.add(phone)
            unique_clients.append(client)
    
    duplicate_count = len(clients) - len(unique_clients)
    return unique_clients, duplicate_count

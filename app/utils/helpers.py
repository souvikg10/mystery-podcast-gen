"""helpers module."""
"""
Helper functions for the application.
"""
import re
from typing import List, Dict, Any
from datetime import datetime

def format_date(date_str: str, format_str: str = "%d/%m/%Y") -> str:
    """
    Format a date string.
    
    Args:
        date_str: The date string to format.
        format_str: The format string.
        
    Returns:
        The formatted date string.
    """
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime(format_str)
    except Exception:
        return date_str

def sanitize_string(text: str) -> str:
    """
    Sanitize a string by removing potentially dangerous characters.
    
    Args:
        text: The string to sanitize.
        
    Returns:
        The sanitized string.
    """
    # Remove any HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove any script tags and their content
    text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text)
    
    # Replace special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text

def paginate_results(items: List[Dict[str, Any]], page: int, page_size: int) -> Dict[str, Any]:
    """
    Paginate a list of items.
    
    Args:
        items: The list of items to paginate.
        page: The page number (1-based).
        page_size: The number of items per page.
        
    Returns:
        A dictionary with pagination metadata and the paginated items.
    """
    # Ensure page is at least 1
    page = max(1, page)
    
    # Calculate start and end indices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Get paginated items
    paginated_items = items[start_idx:end_idx]
    
    # Calculate total pages
    total_pages = (len(items) + page_size - 1) // page_size
    
    return {
        "items": paginated_items,
        "page": page,
        "page_size": page_size,
        "total_items": len(items),
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages
    }

def generate_slug(text: str) -> str:
    """
    Generate a URL-friendly slug from a string.
    
    Args:
        text: The string to generate a slug from.
        
    Returns:
        The generated slug.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    
    # Remove any non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9-]', '', text)
    
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    # Remove leading and trailing hyphens
    text = text.strip('-')
    
    return text
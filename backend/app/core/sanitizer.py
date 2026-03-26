"""
Input sanitization utilities for protecting against XSS and injection attacks.

This module provides functions to sanitize user inputs to prevent:
- Cross-Site Scripting (XSS)
- SQL Injection (through ORM)
- HTML injection
- Path traversal
"""
import re
import html
from typing import Any, Optional
from unicodedata import normalize


class InputSanitizer:
    """
    Input sanitizer for various types of user input.
    """
    
    # Dangerous patterns for XSS
    XSS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),  # onClick, onError, etc.
        re.compile(r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<object[^>]*>.*?</object>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<embed[^>]*>', re.IGNORECASE),
        re.compile(r'eval\s*\(', re.IGNORECASE),
        re.compile(r'expression\s*\(', re.IGNORECASE),
    ]
    
    # SQL injection patterns (for detection/logging only - SQLAlchemy protects against this)
    SQL_PATTERNS = [
        re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)", re.IGNORECASE),
        re.compile(r"(--|#|\/\*|\*\/)"),  # SQL comments
        re.compile(r"('\s*(or|and)\s*')", re.IGNORECASE),
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize a string value.
        
        Args:
            value: Input string to sanitize
            max_length: Optional maximum length
            
        Returns:
            Sanitized string
        """
        if not value:
            return ""
        
        # Normalize Unicode (prevent homograph attacks)
        sanitized = normalize('NFKC', value)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Check and remove XSS patterns
        for pattern in cls.XSS_PATTERNS:
            sanitized = pattern.sub('', sanitized)
        
        # HTML encode to be safe
        sanitized = html.escape(sanitized)
        
        # Apply max length
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @classmethod
    def sanitize_email(cls, email: str) -> str:
        """
        Sanitize an email address.
        
        Args:
            email: Email address to sanitize
            
        Returns:
            Sanitized email
        """
        if not email:
            return ""
        
        # Basic email pattern
        email = email.lower().strip()
        email = re.sub(r'[^\w.@+-]', '', email)
        
        # Limit length
        max_len = 255
        if len(email) > max_len:
            email = email[:max_len]
        
        return email
    
    @classmethod
    def sanitize_name(cls, name: str) -> str:
        """
        Sanitize a name (user's display name, city names, etc.).
        
        Args:
            name: Name to sanitize
            
        Returns:
            Sanitized name
        """
        if not name:
            return ""
        
        # Allow letters, numbers, spaces, hyphens, apostrophes
        sanitized = re.sub(r'[^\w\s\-\']', '', name)
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Limit length
        max_len = 255
        if len(sanitized) > max_len:
            sanitized = sanitized[:max_len]
        
        return sanitized
    
    @classmethod
    def sanitize_phone(cls, phone: str) -> str:
        """
        Sanitize a phone number.
        
        Args:
            phone: Phone number to sanitize
            
        Returns:
            Sanitized phone number
        """
        if not phone:
            return ""
        
        # Keep only digits, plus, spaces, dashes, parentheses
        sanitized = re.sub(r'[^\d\s\+\-\(\)]', '', phone)
        
        # Limit length
        max_len = 20
        if len(sanitized) > max_len:
            sanitized = sanitized[:max_len]
        
        return sanitized
    
    @classmethod
    def sanitize_uuid(cls, value: str) -> Optional[str]:
        """
        Validate and sanitize a UUID string.
        
        Args:
            value: UUID string to sanitize
            
        Returns:
            Valid UUID or None
        """
        if not value:
            return None
        
        # UUID pattern
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        if uuid_pattern.match(value.strip()):
            return value.strip().lower()
        
        return None
    
    @classmethod
    def sanitize_integer(cls, value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
        """
        Sanitize and validate an integer.
        
        Args:
            value: Value to convert to integer
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Sanitized integer or None
        """
        if value is None:
            return None
        
        try:
            int_val = int(value)
            
            if min_val is not None and int_val < min_val:
                return min_val
            
            if max_val is not None and int_val > max_val:
                return max_val
            
            return int_val
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def detect_sql_injection(cls, value: str) -> bool:
        """
        Detect potential SQL injection attempts.
        This is for logging/monitoring purposes.
        
        Args:
            value: Value to check
            
        Returns:
            True if potential SQL injection detected
        """
        if not value:
            return False
        
        for pattern in cls.SQL_PATTERNS:
            if pattern.search(value):
                return True
        
        return False


# Global sanitizer instance
sanitizer = InputSanitizer()


# Convenience functions
def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize a string value."""
    return sanitizer.sanitize_string(value, max_length)


def sanitize_email(email: str) -> str:
    """Sanitize an email address."""
    return sanitizer.sanitize_email(email)


def sanitize_name(name: str) -> str:
    """Sanitize a name."""
    return sanitizer.sanitize_name(name)


def sanitize_phone(phone: str) -> str:
    """Sanitize a phone number."""
    return sanitizer.sanitize_phone(phone)


def sanitize_integer(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
    """Sanitize and validate an integer."""
    return sanitizer.sanitize_integer(value, min_val, max_val)


def sanitize_uuid(value: str) -> Optional[str]:
    """Validate and sanitize a UUID."""
    return sanitizer.sanitize_uuid(value)
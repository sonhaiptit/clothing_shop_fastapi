"""Utility functions and helpers."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import threading


class SimpleRateLimiter:
    """Simple in-memory rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed.
        
        Args:
            key: Unique identifier (e.g., IP address or user ID)
            
        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.window_seconds)
            
            # Clean old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            # Check if limit exceeded
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            # Add current request
            self.requests[key].append(now)
            return True
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests for a key.
        
        Args:
            key: Unique identifier
            
        Returns:
            Number of remaining requests
        """
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.window_seconds)
            
            # Clean old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            return max(0, self.max_requests - len(self.requests[key]))


# Global rate limiter instances
login_limiter = SimpleRateLimiter(max_requests=5, window_seconds=300)  # 5 login attempts per 5 minutes
register_limiter = SimpleRateLimiter(max_requests=3, window_seconds=3600)  # 3 registrations per hour
api_limiter = SimpleRateLimiter(max_requests=60, window_seconds=60)  # 60 requests per minute


def format_price(price: float) -> str:
    """Format price for display.
    
    Args:
        price: Price value
        
    Returns:
        Formatted price string
    """
    return f"{price:,.0f} ₫"


def validate_phone_number(phone: str) -> bool:
    """Validate Vietnamese phone number.
    
    Args:
        phone: Phone number string
        
    Returns:
        True if valid, False otherwise
    """
    # Remove spaces and dashes
    phone = phone.replace(" ", "").replace("-", "")
    
    # Check if all digits
    if not phone.isdigit():
        return False
    
    # Check length (Vietnamese phone numbers are 10-11 digits)
    if len(phone) < 10 or len(phone) > 11:
        return False
    
    # Check if starts with valid prefix
    valid_prefixes = ['03', '05', '07', '08', '09']
    return any(phone.startswith(prefix) for prefix in valid_prefixes)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove dangerous characters
    import re
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = filename.strip()
    return filename

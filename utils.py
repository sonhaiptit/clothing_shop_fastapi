"""Utility functions and helpers."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import re


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
    
    # Vietnamese mobile numbers are 10 digits, landlines can be 10-11
    if len(phone) < 10 or len(phone) > 11:
        return False
    
    # Check if starts with valid prefix for mobile numbers (10 digits)
    if len(phone) == 10:
        # Modern mobile prefixes (03x, 05x, 07x, 08x, 09x series)
        # Also includes old 012x prefix (still in use but being phased out)
        valid_prefixes = [
            '012',  # Old prefix (being phased out)
            '032', '033', '034', '035', '036', '037', '038', '039',
            '056', '058', '059',
            '070', '076', '077', '078', '079',
            '081', '082', '083', '084', '085', '086', '088', '089',
            '090', '091', '092', '093', '094', '096', '097', '098', '099'
        ]
        return any(phone.startswith(prefix) for prefix in valid_prefixes)
    
    # For 11 digit numbers, allow if starts with valid area code
    # This is a simplified check - can be expanded for landlines
    return phone[0] == '0'


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = filename.strip()
    return filename

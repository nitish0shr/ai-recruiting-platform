"""
Logging configuration for the application
"""

import logging
import sys
import json
from typing import Any, Dict
import structlog
from core.config import settings

def setup_logging():
    """Setup structured logging configuration"""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if not settings.DEBUG 
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

class PIIFormatter(logging.Formatter):
    """Custom formatter to redact PII from log messages"""
    
    PII_PATTERNS = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'password[=:]\s*[^\s]+',  # Password
        r'token[=:]\s*[^\s]+',  # Token
        r'api[_-]?key[=:]\s*[^\s]+',  # API Key
    ]
    
    def format(self, record):
        import re
        message = super().format(record)
        
        for pattern in self.PII_PATTERNS:
            message = re.sub(pattern, '[REDACTED]', message, flags=re.IGNORECASE)
        
        return message

def get_logger(name: str = None):
    """Get a structured logger instance"""
    return structlog.get_logger(name)
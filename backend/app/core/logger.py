"""Structured logging configuration for the application.

This module provides JSON logging with request_id context support.
"""
import json
import logging
import sys
import time
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

# Context variable to store request_id across the application
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields (including request_id)
        if hasattr(record, 'extra'):
            for key, value in record.extra.items():
                if value is not None:
                    log_data[key] = value
        
        # Add request_id from context if available
        request_id = request_id_context.get()
        if request_id:
            log_data["request_id"] = request_id
        
        # Add user_id if available
        if hasattr(record, 'user_id'):
            log_data["user_id"] = str(record.user_id)
        
        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    
    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """Custom adapter that adds request_id to all log records."""
    
    def process(self, msg: str, kwargs: dict) -> tuple:
        """Process log message to add extra context."""
        # Add request_id to extra if not already present
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        request_id = request_id_context.get()
        if request_id and 'request_id' not in kwargs['extra']:
            kwargs['extra']['request_id'] = request_id
        
        return msg, kwargs


def get_request_logger(name: str) -> LoggerAdapter:
    """Get a logger adapter that automatically includes request_id.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger adapter with request_id context
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, {})


def set_request_id(request_id: str) -> None:
    """Set the request_id in the context.
    
    Args:
        request_id: The request ID to set
    """
    request_id_context.set(request_id)


def get_request_id() -> Optional[str]:
    """Get the current request_id from context.
    
    Returns:
        Current request_id or None
    """
    return request_id_context.get()


def clear_request_id() -> None:
    """Clear the request_id from context."""
    request_id_context.set(None)

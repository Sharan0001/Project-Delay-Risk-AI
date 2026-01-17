"""
Logging Configuration for the Project Delay Risk AI System.

Provides structured logging setup with:
- Console output with colors (for development)
- JSON formatting option (for production)
- Request ID tracking for API calls
"""

import logging
import sys
from typing import Optional
from datetime import datetime


# Create loggers for different components
logger = logging.getLogger("project_risk")
api_logger = logging.getLogger("project_risk.api")
model_logger = logging.getLogger("project_risk.model")
pipeline_logger = logging.getLogger("project_risk.pipeline")


class ColorFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    json_format: bool = False
) -> None:
    """
    Configures application logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: If True, use JSON formatting for production
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Choose formatter
    if json_format:
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        formatter = ColorFormatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger("project_risk")
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Prevent propagation to root
    root_logger.propagate = False
    
    logger.info("Logging configured at %s level", level)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    request_id: Optional[str] = None
) -> None:
    """
    Logs an API request.
    
    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        request_id: Optional request ID for tracing
    """
    api_logger.info(
        "%s %s -> %d (%.2fms) [%s]",
        method, path, status_code, duration_ms, request_id or "no-id"
    )


def log_analysis(
    task_id: str,
    risk_level: str,
    risk_score: int,
    duration_ms: float
) -> None:
    """
    Logs a risk analysis result.
    
    Args:
        task_id: Task identifier
        risk_level: Computed risk level
        risk_score: Computed risk score
        duration_ms: Analysis duration
    """
    model_logger.info(
        "Analyzed task %s: %s risk (score=%d) in %.2fms",
        task_id, risk_level, risk_score, duration_ms
    )

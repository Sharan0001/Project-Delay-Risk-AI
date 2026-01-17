"""
Custom Exception Classes for the Project Delay Risk AI System.

Provides structured exception handling for different error categories:
- AnalysisError: Issues during risk analysis
- ValidationError: Data validation failures
- ModelError: ML model-related issues
- ConfigurationError: Configuration problems
"""

from typing import Optional, Any, Dict


class BaseAppError(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class AnalysisError(BaseAppError):
    """Raised when risk analysis fails."""
    pass


class ValidationError(BaseAppError):
    """Raised when data validation fails."""
    pass


class ModelNotTrainedError(BaseAppError):
    """Raised when trying to use an untrained model."""
    pass


class ConfigurationError(BaseAppError):
    """Raised when configuration is invalid or missing."""
    pass


class ScenarioNotFoundError(BaseAppError):
    """Raised when an invalid what-if scenario is requested."""
    pass

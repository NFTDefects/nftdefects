"""Error handling and exception management for NFTDefects."""

import logging
from typing import Optional, Any
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NFTDefectsError(Exception):
    """Base exception class for NFTDefects."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 details: Optional[dict] = None):
        self.message = message
        self.severity = severity
        self.details = details or {}
        super().__init__(self.message)


class DetectionError(NFTDefectsError):
    """Exception raised during defect detection."""
    pass


class CompilationError(NFTDefectsError):
    """Exception raised during contract compilation."""
    pass


class AnalysisError(NFTDefectsError):
    """Exception raised during symbolic analysis."""
    pass


class ConfigurationError(NFTDefectsError):
    """Exception raised for configuration issues."""
    pass


class TimeoutError(NFTDefectsError):
    """Exception raised when analysis times out."""
    pass


class ErrorHandler:
    """Centralized error handling and logging."""
    
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
    
    def handle_error(self, error: Exception, context: str = "", 
                    reraise: bool = False) -> bool:
        """
        Handle an error with appropriate logging and optional re-raising.
        
        Args:
            error: The exception to handle
            context: Additional context about where the error occurred
            reraise: Whether to re-raise the exception after handling
            
        Returns:
            True if error was handled successfully, False otherwise
        """
        if isinstance(error, NFTDefectsError):
            return self._handle_nft_defects_error(error, context, reraise)
        else:
            return self._handle_generic_error(error, context, reraise)
    
    def _handle_nft_defects_error(self, error: NFTDefectsError, 
                                 context: str, reraise: bool) -> bool:
        """Handle NFTDefects-specific errors."""
        log_message = f"{context}: {error.message}" if context else error.message
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, extra=error.details)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, extra=error.details)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message, extra=error.details)
        else:  # LOW
            self.logger.info(log_message, extra=error.details)
        
        if reraise:
            raise error
        
        return True
    
    def _handle_generic_error(self, error: Exception, 
                            context: str, reraise: bool) -> bool:
        """Handle generic Python exceptions."""
        log_message = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(log_message, exc_info=True)
        
        if reraise:
            raise error
        
        return True
    
    def log_warning(self, message: str, details: Optional[dict] = None):
        """Log a warning message."""
        self.logger.warning(message, extra=details or {})
    
    def log_info(self, message: str, details: Optional[dict] = None):
        """Log an info message."""
        self.logger.info(message, extra=details or {})
    
    def log_debug(self, message: str, details: Optional[dict] = None):
        """Log a debug message."""
        self.logger.debug(message, extra=details or {})


def safe_execute(func, *args, error_handler: Optional[ErrorHandler] = None, 
                context: str = "", default_return: Any = None, **kwargs):
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        error_handler: ErrorHandler instance to use
        context: Context description for error logging
        default_return: Value to return if function fails
        **kwargs: Keyword arguments for the function
        
    Returns:
        Function result or default_return if function fails
    """
    if error_handler is None:
        error_handler = ErrorHandler()
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.handle_error(e, context)
        return default_return


def create_error_context(operation: str, **kwargs) -> str:
    """Create a standardized error context string."""
    context_parts = [f"Operation: {operation}"]
    for key, value in kwargs.items():
        context_parts.append(f"{key}: {value}")
    return " | ".join(context_parts)
"""
Comprehensive logging and monitoring configuration.

Provides structured logging, performance monitoring, and error tracking.
"""
import logging
import logging.handlers
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum
import os
import sys


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """Log format enumeration."""
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def __init__(self, format_type: LogFormat = LogFormat.DETAILED):
        """
        Initialize structured formatter.
        
        Args:
            format_type: Type of formatting to use
        """
        self.format_type = format_type
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        if self.format_type == LogFormat.JSON:
            return self._format_json(record)
        elif self.format_type == LogFormat.DETAILED:
            return self._format_detailed(record)
        else:
            return self._format_simple(record)
    
    def _format_json(self, record: logging.LogRecord) -> str:
        """Format record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_'):
                log_data[key] = value
        
        return json.dumps(log_data, default=str)
    
    def _format_detailed(self, record: logging.LogRecord) -> str:
        """Format record with detailed information."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Base format
        base_format = f"{timestamp} | {record.levelname:8} | {record.name:20} | {record.getMessage()}"
        
        # Add location info
        location = f"{record.module}:{record.funcName}:{record.lineno}"
        base_format += f" | {location}"
        
        # Add exception info if present
        if record.exc_info:
            base_format += f"\n{traceback.format_exception(*record.exc_info)}"
        
        return base_format
    
    def _format_simple(self, record: logging.LogRecord) -> str:
        """Format record with simple information."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp} | {record.levelname} | {record.getMessage()}"


class PerformanceLogger:
    """Logger for performance monitoring."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize performance logger.
        
        Args:
            logger: Base logger instance
        """
        self.logger = logger
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str) -> None:
        """
        Start timing an operation.
        
        Args:
            operation: Name of the operation to time
        """
        self.start_times[operation] = time.time()
        self.logger.debug(f"Started timing operation: {operation}")
    
    def end_timer(self, operation: str, extra_data: Optional[Dict[str, Any]] = None) -> float:
        """
        End timing an operation and log the duration.
        
        Args:
            operation: Name of the operation
            extra_data: Additional data to log
            
        Returns:
            Duration in seconds
        """
        if operation not in self.start_times:
            self.logger.warning(f"No start time found for operation: {operation}")
            return 0.0
        
        duration = time.time() - self.start_times[operation]
        del self.start_times[operation]
        
        log_data = {
            "operation": operation,
            "duration_seconds": duration,
            "duration_ms": duration * 1000
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        self.logger.info(f"Operation completed: {operation}", extra=log_data)
        return duration
    
    def log_operation(self, operation: str, duration: float, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a completed operation with duration.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            extra_data: Additional data to log
        """
        log_data = {
            "operation": operation,
            "duration_seconds": duration,
            "duration_ms": duration * 1000
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        self.logger.info(f"Operation completed: {operation}", extra=log_data)


class ErrorTracker:
    """Tracker for error monitoring and analysis."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize error tracker.
        
        Args:
            logger: Base logger instance
        """
        self.logger = logger
        self.error_counts: Dict[str, int] = {}
        self.recent_errors: List[Dict[str, Any]] = []
        self.max_recent_errors = 100
    
    def track_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Track an error occurrence.
        
        Args:
            error: Exception that occurred
            context: Additional context information
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Update error counts
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Track recent errors
        error_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
            "traceback": traceback.format_exception(type(error), error, error.__traceback__)
        }
        
        self.recent_errors.append(error_info)
        
        # Keep only recent errors
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors = self.recent_errors[-self.max_recent_errors:]
        
        # Log the error
        self.logger.error(
            f"Error tracked: {error_type}",
            extra={
                "error_type": error_type,
                "error_message": error_message,
                "context": context,
                "error_count": self.error_counts[error_type]
            },
            exc_info=True
        )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of tracked errors.
        
        Returns:
            Error summary dictionary
        """
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": self.error_counts,
            "recent_errors_count": len(self.recent_errors),
            "recent_errors": self.recent_errors[-10:]  # Last 10 errors
        }


class LoggingConfig:
    """Configuration for comprehensive logging."""
    
    def __init__(
        self,
        log_level: LogLevel = LogLevel.INFO,
        log_format: LogFormat = LogFormat.DETAILED,
        log_file: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        enable_console: bool = True,
        enable_performance_logging: bool = True,
        enable_error_tracking: bool = True
    ):
        """
        Initialize logging configuration.
        
        Args:
            log_level: Minimum log level
            log_format: Format for log messages
            log_file: Path to log file (None for no file logging)
            max_file_size: Maximum size of log files before rotation
            backup_count: Number of backup files to keep
            enable_console: Whether to enable console logging
            enable_performance_logging: Whether to enable performance logging
            enable_error_tracking: Whether to enable error tracking
        """
        self.log_level = log_level
        self.log_format = log_format
        self.log_file = log_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_performance_logging = enable_performance_logging
        self.enable_error_tracking = enable_error_tracking
        
        # Create log directory if needed
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self) -> tuple[logging.Logger, PerformanceLogger, ErrorTracker]:
        """
        Set up comprehensive logging.
        
        Returns:
            Tuple of (logger, performance_logger, error_tracker)
        """
        # Create root logger
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, self.log_level.value))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = StructuredFormatter(self.log_format)
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if self.log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Create performance logger
        performance_logger = PerformanceLogger(logger) if self.enable_performance_logging else None
        
        # Create error tracker
        error_tracker = ErrorTracker(logger) if self.enable_error_tracking else None
        
        return logger, performance_logger, error_tracker


def setup_application_logging(
    log_level: str = "INFO",
    log_format: str = "detailed",
    log_file: Optional[str] = "logs/application.log",
    enable_console: bool = True
) -> tuple[logging.Logger, PerformanceLogger, ErrorTracker]:
    """
    Set up application logging with sensible defaults.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (simple, detailed, json)
        log_file: Path to log file
        enable_console: Whether to enable console logging
        
    Returns:
        Tuple of (logger, performance_logger, error_tracker)
    """
    config = LoggingConfig(
        log_level=LogLevel(log_level.upper()),
        log_format=LogFormat(log_format.lower()),
        log_file=log_file,
        enable_console=enable_console
    )
    
    return config.setup_logging()


# Global logging instances
_global_logger: Optional[logging.Logger] = None
_global_performance_logger: Optional[PerformanceLogger] = None
_global_error_tracker: Optional[ErrorTracker] = None


def get_logger() -> logging.Logger:
    """Get the global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger, _, _ = setup_application_logging()
    return _global_logger


def get_performance_logger() -> PerformanceLogger:
    """Get the global performance logger instance."""
    global _global_performance_logger
    if _global_performance_logger is None:
        _, _global_performance_logger, _ = setup_application_logging()
    return _global_performance_logger


def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker instance."""
    global _global_error_tracker
    if _global_error_tracker is None:
        _, _, _global_error_tracker = setup_application_logging()
    return _global_error_tracker


def log_function_call(func_name: str, args: tuple, kwargs: dict, result: Any = None, duration: float = None):
    """
    Log a function call with its parameters and result.
    
    Args:
        func_name: Name of the function
        args: Function arguments
        kwargs: Function keyword arguments
        result: Function result
        duration: Function execution duration
    """
    logger = get_logger()
    
    log_data = {
        "function": func_name,
        "args": str(args)[:200],  # Truncate long arguments
        "kwargs": {k: str(v)[:100] for k, v in kwargs.items()},
        "duration": duration
    }
    
    if result is not None:
        log_data["result_type"] = type(result).__name__
        log_data["result_preview"] = str(result)[:200]
    
    logger.info(f"Function call: {func_name}", extra=log_data)


def log_api_request(method: str, url: str, status_code: int, duration: float, response_size: int = None):
    """
    Log an API request.
    
    Args:
        method: HTTP method
        url: Request URL
        status_code: Response status code
        duration: Request duration
        response_size: Response size in bytes
    """
    logger = get_logger()
    
    log_data = {
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration": duration,
        "response_size": response_size
    }
    
    level = logging.INFO if status_code < 400 else logging.WARNING
    logger.log(level, f"API request: {method} {url}", extra=log_data)


def log_database_operation(operation: str, table: str, duration: float, rows_affected: int = None):
    """
    Log a database operation.
    
    Args:
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration: Operation duration
        rows_affected: Number of rows affected
    """
    logger = get_logger()
    
    log_data = {
        "operation": operation,
        "table": table,
        "duration": duration,
        "rows_affected": rows_affected
    }
    
    logger.info(f"Database operation: {operation} {table}", extra=log_data)

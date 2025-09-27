"""
Unit tests for logging configuration and monitoring.
"""
import pytest
import tempfile
import os
import json
import time
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.utils.logging_config import (
    LoggingConfig,
    LogLevel,
    LogFormat,
    StructuredFormatter,
    PerformanceLogger,
    ErrorTracker,
    setup_application_logging,
    get_logger,
    get_performance_logger,
    get_error_tracker,
    log_function_call,
    log_api_request,
    log_database_operation
)


class TestLoggingConfig:
    """Test logging configuration."""
    
    def test_logging_config_initialization(self):
        """Test logging config initialization."""
        config = LoggingConfig(
            log_level=LogLevel.DEBUG,
            log_format=LogFormat.JSON,
            log_file="test.log",
            max_file_size=1024,
            backup_count=3,
            enable_console=False,
            enable_performance_logging=True,
            enable_error_tracking=True
        )
        
        assert config.log_level == LogLevel.DEBUG
        assert config.log_format == LogFormat.JSON
        assert config.log_file == "test.log"
        assert config.max_file_size == 1024
        assert config.backup_count == 3
        assert config.enable_console is False
        assert config.enable_performance_logging is True
        assert config.enable_error_tracking is True
    
    def test_logging_config_defaults(self):
        """Test logging config default values."""
        config = LoggingConfig()
        
        assert config.log_level == LogLevel.INFO
        assert config.log_format == LogFormat.DETAILED
        assert config.log_file is None
        assert config.max_file_size == 10 * 1024 * 1024
        assert config.backup_count == 5
        assert config.enable_console is True
        assert config.enable_performance_logging is True
        assert config.enable_error_tracking is True


class TestStructuredFormatter:
    """Test structured formatter."""
    
    def test_simple_format(self):
        """Test simple formatting."""
        formatter = StructuredFormatter(LogFormat.SIMPLE)
        record = MagicMock()
        record.levelname = "INFO"
        record.getMessage.return_value = "Test message"
        
        with patch('src.utils.logging_config.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.strftime.return_value = "2024-01-01 12:00:00"
            result = formatter.format(record)
            
            assert "2024-01-01 12:00:00" in result
            assert "INFO" in result
            assert "Test message" in result
    
    def test_detailed_format(self):
        """Test detailed formatting."""
        formatter = StructuredFormatter(LogFormat.DETAILED)
        record = MagicMock()
        record.levelname = "ERROR"
        record.name = "test_logger"
        record.getMessage.return_value = "Test error"
        record.module = "test_module"
        record.funcName = "test_function"
        record.lineno = 42
        record.exc_info = None
        
        with patch('src.utils.logging_config.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.strftime.return_value = "2024-01-01 12:00:00.123"
            result = formatter.format(record)
            
            assert "2024-01-01 12:00:00" in result
            assert "ERROR" in result
            assert "Test error" in result
            assert "test_module:test_function:42" in result
    
    def test_json_format(self):
        """Test JSON formatting."""
        formatter = StructuredFormatter(LogFormat.JSON)
        
        # Create a real logging record instead of mock
        import logging
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)
        
        # Create a log record manually
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test_module.py",
            lineno=42,
            msg="Test warning",
            args=(),
            exc_info=None
        )
        record.thread = 123
        record.process = 456
        record.funcName = "test_function"
        record.module = "test_module"
        
        with patch('src.utils.logging_config.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            result = formatter.format(record)
            
            # Parse JSON result
            log_data = json.loads(result)
            
            assert log_data["timestamp"] == "2024-01-01T12:00:00"
            assert log_data["level"] == "WARNING"
            assert log_data["logger"] == "test_logger"
            assert log_data["message"] == "Test warning"
            assert log_data["module"] == "test_module"
            assert log_data["function"] == "test_function"
            assert log_data["line"] == 42
            assert log_data["thread"] == 123
            assert log_data["process"] == 456


class TestPerformanceLogger:
    """Test performance logger."""
    
    def test_performance_logger_initialization(self):
        """Test performance logger initialization."""
        mock_logger = MagicMock()
        perf_logger = PerformanceLogger(mock_logger)
        
        assert perf_logger.logger == mock_logger
        assert perf_logger.start_times == {}
    
    def test_start_timer(self):
        """Test starting a timer."""
        mock_logger = MagicMock()
        perf_logger = PerformanceLogger(mock_logger)
        
        with patch('time.time', return_value=1000.0):
            perf_logger.start_timer("test_operation")
            
            assert "test_operation" in perf_logger.start_times
            assert perf_logger.start_times["test_operation"] == 1000.0
            mock_logger.debug.assert_called_once()
    
    def test_end_timer(self):
        """Test ending a timer."""
        mock_logger = MagicMock()
        perf_logger = PerformanceLogger(mock_logger)
        
        # Set up start time
        perf_logger.start_times["test_operation"] = 1000.0
        
        with patch('time.time', return_value=1002.5):
            duration = perf_logger.end_timer("test_operation")
            
            assert duration == 2.5
            assert "test_operation" not in perf_logger.start_times
            mock_logger.info.assert_called_once()
    
    def test_end_timer_with_extra_data(self):
        """Test ending a timer with extra data."""
        mock_logger = MagicMock()
        perf_logger = PerformanceLogger(mock_logger)
        
        # Set up start time
        perf_logger.start_times["test_operation"] = 1000.0
        
        with patch('time.time', return_value=1002.5):
            extra_data = {"status": "success", "items_processed": 100}
            duration = perf_logger.end_timer("test_operation", extra_data)
            
            assert duration == 2.5
            mock_logger.info.assert_called_once()
            
            # Check that extra data was passed to logger
            call_args = mock_logger.info.call_args
            assert "status" in call_args[1]["extra"]
            assert "items_processed" in call_args[1]["extra"]
    
    def test_end_timer_missing_operation(self):
        """Test ending a timer for non-existent operation."""
        mock_logger = MagicMock()
        perf_logger = PerformanceLogger(mock_logger)
        
        duration = perf_logger.end_timer("missing_operation")
        
        assert duration == 0.0
        mock_logger.warning.assert_called_once()
    
    def test_log_operation(self):
        """Test logging a completed operation."""
        mock_logger = MagicMock()
        perf_logger = PerformanceLogger(mock_logger)
        
        extra_data = {"status": "success"}
        perf_logger.log_operation("test_operation", 2.5, extra_data)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert "test_operation" in call_args[0][0]
        assert call_args[1]["extra"]["duration_seconds"] == 2.5
        assert call_args[1]["extra"]["status"] == "success"


class TestErrorTracker:
    """Test error tracker."""
    
    def test_error_tracker_initialization(self):
        """Test error tracker initialization."""
        mock_logger = MagicMock()
        error_tracker = ErrorTracker(mock_logger)
        
        assert error_tracker.logger == mock_logger
        assert error_tracker.error_counts == {}
        assert error_tracker.recent_errors == []
        assert error_tracker.max_recent_errors == 100
    
    def test_track_error(self):
        """Test tracking an error."""
        mock_logger = MagicMock()
        error_tracker = ErrorTracker(mock_logger)
        
        error = ValueError("Test error")
        context = {"operation": "test", "user_id": 123}
        
        with patch('src.utils.logging_config.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            error_tracker.track_error(error, context)
            
            # Check error counts
            assert error_tracker.error_counts["ValueError"] == 1
            
            # Check recent errors
            assert len(error_tracker.recent_errors) == 1
            recent_error = error_tracker.recent_errors[0]
            assert recent_error["error_type"] == "ValueError"
            assert recent_error["error_message"] == "Test error"
            assert recent_error["context"] == context
            
            # Check logger was called
            mock_logger.error.assert_called_once()
    
    def test_track_multiple_errors(self):
        """Test tracking multiple errors."""
        mock_logger = MagicMock()
        error_tracker = ErrorTracker(mock_logger)
        
        # Track first error
        error1 = ValueError("Error 1")
        error_tracker.track_error(error1)
        
        # Track second error
        error2 = TypeError("Error 2")
        error_tracker.track_error(error2)
        
        # Track same error type again
        error3 = ValueError("Error 3")
        error_tracker.track_error(error3)
        
        # Check error counts
        assert error_tracker.error_counts["ValueError"] == 2
        assert error_tracker.error_counts["TypeError"] == 1
        
        # Check recent errors
        assert len(error_tracker.recent_errors) == 3
    
    def test_get_error_summary(self):
        """Test getting error summary."""
        mock_logger = MagicMock()
        error_tracker = ErrorTracker(mock_logger)
        
        # Track some errors
        error_tracker.track_error(ValueError("Error 1"))
        error_tracker.track_error(ValueError("Error 2"))
        error_tracker.track_error(TypeError("Error 3"))
        
        summary = error_tracker.get_error_summary()
        
        assert summary["total_errors"] == 3
        assert summary["error_types"]["ValueError"] == 2
        assert summary["error_types"]["TypeError"] == 1
        assert summary["recent_errors_count"] == 3
        assert len(summary["recent_errors"]) == 3
    
    def test_recent_errors_limit(self):
        """Test that recent errors are limited."""
        mock_logger = MagicMock()
        error_tracker = ErrorTracker(mock_logger)
        error_tracker.max_recent_errors = 3
        
        # Track more errors than the limit
        for i in range(5):
            error_tracker.track_error(ValueError(f"Error {i}"))
        
        # Should only keep the last 3 errors
        assert len(error_tracker.recent_errors) == 3
        assert error_tracker.recent_errors[0]["error_message"] == "Error 2"
        assert error_tracker.recent_errors[2]["error_message"] == "Error 4"


class TestLoggingSetup:
    """Test logging setup functions."""
    
    def test_setup_application_logging(self):
        """Test setting up application logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            logger, perf_logger, error_tracker = setup_application_logging(
                log_level="DEBUG",
                log_format="simple",
                log_file=log_file,
                enable_console=False
            )
            
            assert logger is not None
            assert perf_logger is not None
            assert error_tracker is not None
            
            # Test that logging works
            logger.info("Test message")
            
            # Check that log file was created
            assert os.path.exists(log_file)
    
    def test_get_logger_functions(self):
        """Test global logger functions."""
        # Test that functions return logger instances
        logger = get_logger()
        assert logger is not None
        
        perf_logger = get_performance_logger()
        assert perf_logger is not None
        
        error_tracker = get_error_tracker()
        assert error_tracker is not None


class TestLoggingHelpers:
    """Test logging helper functions."""
    
    def test_log_function_call(self):
        """Test logging function calls."""
        with patch('src.utils.logging_config.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_function_call(
                "test_function",
                ("arg1", "arg2"),
                {"kwarg1": "value1"},
                "result",
                1.5
            )
            
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "test_function" in call_args[0][0]
            assert call_args[1]["extra"]["function"] == "test_function"
            assert call_args[1]["extra"]["duration"] == 1.5
    
    def test_log_api_request(self):
        """Test logging API requests."""
        with patch('src.utils.logging_config.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Mock the logger to return a callable log method
            mock_logger.log = MagicMock()
            
            log_api_request("GET", "/api/test", 200, 0.5, 1024)
            
            # Check that log was called
            mock_logger.log.assert_called_once()
            call_args = mock_logger.log.call_args
            assert "GET /api/test" in call_args[0][1]  # message is second argument
            assert call_args[1]["extra"]["method"] == "GET"
            assert call_args[1]["extra"]["status_code"] == 200
    
    def test_log_database_operation(self):
        """Test logging database operations."""
        with patch('src.utils.logging_config.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_database_operation("SELECT", "users", 0.1, 100)
            
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "SELECT users" in call_args[0][0]
            assert call_args[1]["extra"]["operation"] == "SELECT"
            assert call_args[1]["extra"]["table"] == "users"

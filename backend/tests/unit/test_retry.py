"""
Unit tests for retry logic and exponential backoff.
"""
import pytest
import time
from unittest.mock import patch, MagicMock

from src.utils.retry import (
    RetryConfig, 
    RetryStrategy, 
    RetryError, 
    retry_with_backoff,
    RetryManager,
    calculate_delay,
    API_RETRY_CONFIG,
    DATABASE_RETRY_CONFIG,
    LLM_RETRY_CONFIG
)


class TestRetryConfig:
    """Test retry configuration."""
    
    def test_retry_config_initialization(self):
        """Test retry config initialization."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            max_delay=30.0,
            strategy=RetryStrategy.EXPONENTIAL,
            jitter=True,
            backoff_multiplier=3.0
        )
        
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 30.0
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.jitter is True
        assert config.backoff_multiplier == 3.0
    
    def test_retry_config_defaults(self):
        """Test retry config default values."""
        config = RetryConfig()
        
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.jitter is True
        assert config.backoff_multiplier == 2.0


class TestCalculateDelay:
    """Test delay calculation."""
    
    def test_calculate_delay_fixed(self):
        """Test fixed delay calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.FIXED,
            base_delay=2.0,
            jitter=False
        )
        
        # First attempt should have no delay
        assert calculate_delay(0, config) == 0.0
        
        # Subsequent attempts should have fixed delay
        assert calculate_delay(1, config) == 2.0
        assert calculate_delay(2, config) == 2.0
        assert calculate_delay(3, config) == 2.0
    
    def test_calculate_delay_linear(self):
        """Test linear delay calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.LINEAR,
            base_delay=1.0,
            jitter=False
        )
        
        assert calculate_delay(0, config) == 0.0
        assert calculate_delay(1, config) == 1.0
        assert calculate_delay(2, config) == 2.0
        assert calculate_delay(3, config) == 3.0
    
    def test_calculate_delay_exponential(self):
        """Test exponential delay calculation."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=1.0,
            backoff_multiplier=2.0,
            jitter=False
        )
        
        assert calculate_delay(0, config) == 0.0
        assert calculate_delay(1, config) == 1.0  # 1.0 * 2^0
        assert calculate_delay(2, config) == 2.0  # 1.0 * 2^1
        assert calculate_delay(3, config) == 4.0  # 1.0 * 2^2
        assert calculate_delay(4, config) == 8.0  # 1.0 * 2^3
    
    def test_calculate_delay_max_limit(self):
        """Test delay calculation with max limit."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=1.0,
            max_delay=5.0,
            jitter=False
        )
        
        assert calculate_delay(0, config) == 0.0
        assert calculate_delay(1, config) == 1.0
        assert calculate_delay(2, config) == 2.0
        assert calculate_delay(3, config) == 4.0
        assert calculate_delay(4, config) == 5.0  # Limited by max_delay
        assert calculate_delay(5, config) == 5.0  # Limited by max_delay
    
    def test_calculate_delay_jitter(self):
        """Test delay calculation with jitter."""
        config = RetryConfig(
            strategy=RetryStrategy.FIXED,
            base_delay=10.0,
            jitter=True
        )
        
        # Run multiple times to test jitter
        delays = [calculate_delay(1, config) for _ in range(10)]
        
        # All delays should be close to 10.0 but not exactly the same
        for delay in delays:
            assert 9.0 <= delay <= 11.0  # 10% jitter
        
        # Should have some variation
        assert len(set(delays)) > 1


class TestRetryDecorator:
    """Test retry decorator."""
    
    def test_retry_decorator_success(self):
        """Test retry decorator with successful function."""
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        
        @retry_with_backoff(config=config)
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_retry_decorator_failure(self):
        """Test retry decorator with failing function."""
        config = RetryConfig(max_attempts=2, base_delay=0.01)
        
        @retry_with_backoff(config=config)
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(RetryError) as exc_info:
            failing_function()
        
        assert "failed after 2 attempts" in str(exc_info.value)
        assert exc_info.value.attempts == 2
    
    def test_retry_decorator_success_after_retry(self):
        """Test retry decorator with function that succeeds after retries."""
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        call_count = 0
        
        @retry_with_backoff(config=config)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert call_count == 3
    
    def test_retry_decorator_non_retryable_exception(self):
        """Test retry decorator with non-retryable exception."""
        config = RetryConfig(
            max_attempts=3,
            base_delay=0.01,
            retryable_exceptions=(ValueError,)
        )
        
        @retry_with_backoff(config=config)
        def function_with_non_retryable_error():
            raise TypeError("Non-retryable error")
        
        with pytest.raises(TypeError):
            function_with_non_retryable_error()
    
    def test_retry_decorator_timing(self):
        """Test retry decorator timing."""
        config = RetryConfig(
            max_attempts=3,
            base_delay=0.1,
            strategy=RetryStrategy.EXPONENTIAL,
            jitter=False
        )
        
        call_times = []
        
        @retry_with_backoff(config=config)
        def timing_function():
            call_times.append(time.time())
            raise ValueError("Test error")
        
        start_time = time.time()
        
        with pytest.raises(RetryError):
            timing_function()
        
        # Should have 3 calls with exponential delays
        assert len(call_times) == 3
        
        # Check that delays are approximately correct
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert 0.05 <= delay1 <= 0.15  # Allow some tolerance
        
        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            assert 0.15 <= delay2 <= 0.25  # Exponential backoff


class TestRetryManager:
    """Test retry manager."""
    
    def test_retry_manager_initialization(self):
        """Test retry manager initialization."""
        manager = RetryManager()
        assert manager.default_config is not None
        
        custom_config = RetryConfig(max_attempts=5)
        manager = RetryManager(default_config=custom_config)
        assert manager.default_config == custom_config
    
    def test_execute_with_retry_success(self):
        """Test execute with retry success."""
        manager = RetryManager()
        
        def successful_function(x, y):
            return x + y
        
        result = manager.execute_with_retry(successful_function, 2, 3)
        assert result == 5
    
    def test_execute_with_retry_failure(self):
        """Test execute with retry failure."""
        manager = RetryManager()
        
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(RetryError):
            manager.execute_with_retry(failing_function)
    
    def test_execute_with_retry_custom_config(self):
        """Test execute with retry using custom config."""
        manager = RetryManager()
        custom_config = RetryConfig(max_attempts=2, base_delay=0.01)
        
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(RetryError) as exc_info:
            manager.execute_with_retry(failing_function, config=custom_config)
        
        assert exc_info.value.attempts == 2
    
    def test_create_retry_config(self):
        """Test create retry config."""
        manager = RetryManager()
        
        config = manager.create_retry_config(
            max_attempts=5,
            base_delay=2.0,
            strategy=RetryStrategy.LINEAR
        )
        
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.strategy == RetryStrategy.LINEAR


class TestPredefinedConfigs:
    """Test predefined retry configurations."""
    
    def test_api_retry_config(self):
        """Test API retry configuration."""
        assert API_RETRY_CONFIG.max_attempts == 3
        assert API_RETRY_CONFIG.base_delay == 1.0
        assert API_RETRY_CONFIG.max_delay == 30.0
        assert API_RETRY_CONFIG.strategy == RetryStrategy.EXPONENTIAL
        assert API_RETRY_CONFIG.jitter is True
    
    def test_database_retry_config(self):
        """Test database retry configuration."""
        assert DATABASE_RETRY_CONFIG.max_attempts == 5
        assert DATABASE_RETRY_CONFIG.base_delay == 0.5
        assert DATABASE_RETRY_CONFIG.max_delay == 10.0
        assert DATABASE_RETRY_CONFIG.strategy == RetryStrategy.EXPONENTIAL
        assert DATABASE_RETRY_CONFIG.jitter is True
    
    def test_llm_retry_config(self):
        """Test LLM retry configuration."""
        assert LLM_RETRY_CONFIG.max_attempts == 3
        assert LLM_RETRY_CONFIG.base_delay == 2.0
        assert LLM_RETRY_CONFIG.max_delay == 60.0
        assert LLM_RETRY_CONFIG.strategy == RetryStrategy.EXPONENTIAL
        assert LLM_RETRY_CONFIG.jitter is True


class TestRetryError:
    """Test retry error."""
    
    def test_retry_error_initialization(self):
        """Test retry error initialization."""
        original_error = ValueError("Original error")
        retry_error = RetryError("Retry failed", original_error, 3)
        
        assert "Retry failed" in str(retry_error)
        assert "3" in str(retry_error)
        assert "Original error" in str(retry_error)
        assert retry_error.last_exception == original_error
        assert retry_error.attempts == 3
    
    def test_retry_error_string_representation(self):
        """Test retry error string representation."""
        original_error = ValueError("Original error")
        retry_error = RetryError("Retry failed", original_error, 3)
        
        assert "Retry failed" in str(retry_error)
        assert "3" in str(retry_error)

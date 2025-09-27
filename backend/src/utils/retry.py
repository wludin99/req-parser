"""
Retry logic and exponential backoff utilities.

Provides robust retry mechanisms for API calls and other operations.
"""
import time
import random
import logging
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps
from enum import Enum


class RetryStrategy(Enum):
    """Retry strategy options."""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: bool = True,
        backoff_multiplier: float = 2.0,
        retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay in seconds for first retry
            max_delay: Maximum delay in seconds
            strategy: Retry strategy (fixed, exponential, linear)
            jitter: Whether to add random jitter to delays
            backoff_multiplier: Multiplier for exponential backoff
            retryable_exceptions: Tuple of exception types that should trigger retries
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.jitter = jitter
        self.backoff_multiplier = backoff_multiplier
        self.retryable_exceptions = retryable_exceptions


class RetryError(Exception):
    """Exception raised when all retry attempts are exhausted."""
    
    def __init__(self, message: str, last_exception: Exception, attempts: int):
        super().__init__(message)
        self.last_exception = last_exception
        self.attempts = attempts
    
    def __str__(self):
        return f"{super().__str__()} (attempts: {self.attempts}, last error: {self.last_exception})"


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """
    Calculate delay for a given attempt.
    
    Args:
        attempt: Current attempt number (0-based)
        config: Retry configuration
        
    Returns:
        Delay in seconds
    """
    if attempt == 0:
        return 0.0
    
    if config.strategy == RetryStrategy.FIXED:
        delay = config.base_delay
    elif config.strategy == RetryStrategy.LINEAR:
        delay = config.base_delay * attempt
    elif config.strategy == RetryStrategy.EXPONENTIAL:
        delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
    else:
        delay = config.base_delay
    
    # Apply maximum delay limit
    delay = min(delay, config.max_delay)
    
    # Add jitter if enabled
    if config.jitter:
        jitter_range = delay * 0.1  # 10% jitter
        delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0.0, delay)


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    logger: Optional[logging.Logger] = None
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        config: Retry configuration
        logger: Logger for retry attempts
        
    Returns:
        Decorated function
    """
    if config is None:
        config = RetryConfig()
    
    if logger is None:
        logger = logging.getLogger(__name__)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    if attempt > 0:
                        delay = calculate_delay(attempt, config)
                        logger.info(f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1}/{config.max_attempts})")
                        time.sleep(delay)
                    
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if this exception should trigger a retry
                    if not isinstance(e, config.retryable_exceptions):
                        logger.error(f"Non-retryable exception in {func.__name__}: {e}")
                        raise
                    
                    if attempt == config.max_attempts - 1:
                        logger.error(f"All retry attempts exhausted for {func.__name__}")
                        raise RetryError(
                            f"Function {func.__name__} failed after {config.max_attempts} attempts",
                            last_exception,
                            config.max_attempts
                        )
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
            
            # This should never be reached, but just in case
            raise RetryError(
                f"Function {func.__name__} failed after {config.max_attempts} attempts",
                last_exception,
                config.max_attempts
            )
        
        return wrapper
    return decorator


class RetryManager:
    """Manager for retry operations with different configurations."""
    
    def __init__(self, default_config: Optional[RetryConfig] = None):
        """
        Initialize retry manager.
        
        Args:
            default_config: Default retry configuration
        """
        self.default_config = default_config or RetryConfig()
        self.logger = logging.getLogger(__name__)
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        config: Optional[RetryConfig] = None,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            config: Retry configuration (uses default if None)
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            RetryError: If all retry attempts are exhausted
        """
        if config is None:
            config = self.default_config
        
        last_exception = None
        
        for attempt in range(config.max_attempts):
            try:
                if attempt > 0:
                    delay = calculate_delay(attempt, config)
                    self.logger.info(f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1}/{config.max_attempts})")
                    time.sleep(delay)
                
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Check if this exception should trigger a retry
                if not isinstance(e, config.retryable_exceptions):
                    self.logger.error(f"Non-retryable exception in {func.__name__}: {e}")
                    raise
                
                if attempt == config.max_attempts - 1:
                    self.logger.error(f"All retry attempts exhausted for {func.__name__}")
                    raise RetryError(
                        f"Function {func.__name__} failed after {config.max_attempts} attempts",
                        last_exception,
                        config.max_attempts
                    )
                
                self.logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
        
        # This should never be reached
        raise RetryError(
            f"Function {func.__name__} failed after {config.max_attempts} attempts",
            last_exception,
            config.max_attempts
        )
    
    def create_retry_config(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: bool = True,
        backoff_multiplier: float = 2.0,
        retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ) -> RetryConfig:
        """
        Create a retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay in seconds for first retry
            max_delay: Maximum delay in seconds
            strategy: Retry strategy
            jitter: Whether to add random jitter to delays
            backoff_multiplier: Multiplier for exponential backoff
            retryable_exceptions: Tuple of exception types that should trigger retries
            
        Returns:
            Retry configuration
        """
        return RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=strategy,
            jitter=jitter,
            backoff_multiplier=backoff_multiplier,
            retryable_exceptions=retryable_exceptions
        )


# Predefined retry configurations for common scenarios
API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,
    retryable_exceptions=(ConnectionError, TimeoutError, Exception)
)

DATABASE_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=0.5,
    max_delay=10.0,
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,
    retryable_exceptions=(ConnectionError, TimeoutError, Exception)
)

LLM_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=60.0,
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,
    retryable_exceptions=(ConnectionError, TimeoutError, Exception)
)

# Global retry manager instance
retry_manager = RetryManager()

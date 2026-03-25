"""
Error Handler Module
Graceful error recovery, retry logic, and agent health monitoring.
"""
import logging
import time
import traceback
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentHealth(Enum):
    """Agent health states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRASHED = "crashed"


class RetryStrategy:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry strategy.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to prevent thundering herd
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        import random
        
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            delay *= (0.5 + random.random())  # Add 0-50% jitter
        
        return delay


class ErrorHandler:
    """Centralized error handling and recovery."""
    
    def __init__(self):
        """Initialize error handler."""
        self.error_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        self.agent_health_status: Dict[str, AgentHealth] = {}
        self.agent_error_counts: Dict[str, int] = {}
        self.agent_last_success: Dict[str, datetime] = {}
    
    def log_error(
        self,
        error: Exception,
        context: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an error with context and metadata.
        
        Args:
            error: The exception that occurred
            context: Context description (what was being attempted)
            severity: Error severity level
            agent_id: ID of the agent that encountered the error
            metadata: Additional error metadata
        """
        error_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'severity': severity.value,
            'agent_id': agent_id,
            'traceback': traceback.format_exc(),
            'metadata': metadata or {}
        }
        
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
        
        # Update agent error count
        if agent_id:
            self.agent_error_counts[agent_id] = self.agent_error_counts.get(agent_id, 0) + 1
            self._update_agent_health(agent_id)
        
        # Log appropriately based on severity
        log_message = f"[{severity.value.upper()}] {context}: {error}"
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=True)
        elif severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=True)
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _update_agent_health(self, agent_id: str):
        """Update agent health based on error patterns."""
        error_count = self.agent_error_counts.get(agent_id, 0)
        last_success = self.agent_last_success.get(agent_id)
        
        # Check time since last success
        time_since_success = None
        if last_success:
            time_since_success = datetime.utcnow() - last_success
        
        # Determine health status
        if error_count == 0:
            health = AgentHealth.HEALTHY
        elif error_count <= 3:
            health = AgentHealth.DEGRADED
        elif error_count <= 10:
            health = AgentHealth.UNHEALTHY
        else:
            health = AgentHealth.CRASHED
        
        # Override if agent hasn't succeeded in a while
        if time_since_success and time_since_success > timedelta(minutes=30):
            if health == AgentHealth.HEALTHY:
                health = AgentHealth.DEGRADED
            elif health == AgentHealth.DEGRADED:
                health = AgentHealth.UNHEALTHY
        
        old_health = self.agent_health_status.get(agent_id)
        self.agent_health_status[agent_id] = health
        
        if old_health != health:
            logger.warning(f"Agent {agent_id} health changed: {old_health} -> {health}")
    
    def record_success(self, agent_id: str):
        """Record successful agent operation."""
        self.agent_last_success[agent_id] = datetime.utcnow()
        # Reset error count on success
        if agent_id in self.agent_error_counts:
            self.agent_error_counts[agent_id] = max(0, self.agent_error_counts[agent_id] - 1)
        self._update_agent_health(agent_id)
    
    def get_agent_health(self, agent_id: str) -> AgentHealth:
        """Get current health status of an agent."""
        return self.agent_health_status.get(agent_id, AgentHealth.HEALTHY)
    
    def should_restart_agent(self, agent_id: str) -> bool:
        """Determine if an agent should be restarted based on health."""
        health = self.get_agent_health(agent_id)
        return health in [AgentHealth.UNHEALTHY, AgentHealth.CRASHED]
    
    def get_error_summary(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get error summary statistics.
        
        Args:
            agent_id: Optional agent ID to filter by
            
        Returns:
            Dictionary with error statistics
        """
        errors = self.error_history
        if agent_id:
            errors = [e for e in errors if e.get('agent_id') == agent_id]
        
        if not errors:
            return {'total_errors': 0}
        
        # Count by severity
        severity_counts = {}
        error_type_counts = {}
        
        for error in errors:
            severity = error['severity']
            error_type = error['error_type']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
        
        return {
            'total_errors': len(errors),
            'by_severity': severity_counts,
            'by_type': error_type_counts,
            'recent_errors': errors[-10:]  # Last 10 errors
        }


# Global error handler instance
error_handler = ErrorHandler()


def with_retry(
    strategy: Optional[RetryStrategy] = None,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None,
    agent_id: Optional[str] = None
):
    """
    Decorator to add retry logic to functions.
    
    Args:
        strategy: Retry strategy configuration
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry
        agent_id: Optional agent ID for health tracking
    
    Example:
        @with_retry(strategy=RetryStrategy(max_attempts=5))
        def unreliable_api_call():
            # ... your code here
    """
    if strategy is None:
        strategy = RetryStrategy()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(strategy.max_attempts):
                try:
                    result = func(*args, **kwargs)
                    
                    # Record success if agent_id provided
                    if agent_id:
                        error_handler.record_success(agent_id)
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    # Log error
                    error_handler.log_error(
                        error=e,
                        context=f"Function {func.__name__} (attempt {attempt + 1}/{strategy.max_attempts})",
                        severity=ErrorSeverity.MEDIUM if attempt < strategy.max_attempts - 1 else ErrorSeverity.HIGH,
                        agent_id=agent_id
                    )
                    
                    # Check if we should retry
                    if attempt < strategy.max_attempts - 1:
                        delay = strategy.get_delay(attempt)
                        logger.info(f"Retrying {func.__name__} in {delay:.2f}s...")
                        
                        if on_retry:
                            on_retry(attempt, e)
                        
                        time.sleep(delay)
                    else:
                        logger.error(f"Function {func.__name__} failed after {strategy.max_attempts} attempts")
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    *args,
    fallback_value: Any = None,
    context: str = None,
    agent_id: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for function
        fallback_value: Value to return on error
        context: Context description for error logging
        agent_id: Optional agent ID for health tracking
        **kwargs: Keyword arguments for function
        
    Returns:
        Function result or fallback_value on error
    """
    try:
        result = func(*args, **kwargs)
        if agent_id:
            error_handler.record_success(agent_id)
        return result
    except Exception as e:
        error_handler.log_error(
            error=e,
            context=context or f"Executing {func.__name__}",
            severity=ErrorSeverity.MEDIUM,
            agent_id=agent_id
        )
        return fallback_value


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting reset
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        if self.state == 'open':
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = 'half-open'
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
                logger.info("Circuit breaker reset to closed state")
            return result
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise e

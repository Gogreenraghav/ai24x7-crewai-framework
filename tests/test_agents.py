"""
Unit tests for agent functionality.
"""
import unittest
from unittest.mock import Mock, patch
from src.core.error_handler import error_handler, with_retry, RetryStrategy, safe_execute
from src.core.task_queue import Task, TaskPriority, TaskStatus, InMemoryTaskQueue


class TestErrorHandler(unittest.TestCase):
    """Test error handler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        error_handler.error_history.clear()
        error_handler.agent_error_counts.clear()
        error_handler.agent_health_status.clear()
    
    def test_log_error(self):
        """Test error logging."""
        error = ValueError("Test error")
        error_handler.log_error(
            error=error,
            context="Test context",
            agent_id="test_agent"
        )
        
        self.assertEqual(len(error_handler.error_history), 1)
        self.assertEqual(error_handler.error_history[0]['error_type'], 'ValueError')
        self.assertEqual(error_handler.agent_error_counts['test_agent'], 1)
    
    def test_record_success(self):
        """Test success recording."""
        error_handler.agent_error_counts['test_agent'] = 5
        error_handler.record_success('test_agent')
        
        self.assertEqual(error_handler.agent_error_counts['test_agent'], 4)
        self.assertIsNotNone(error_handler.agent_last_success.get('test_agent'))
    
    def test_retry_decorator(self):
        """Test retry decorator."""
        call_count = 0
        
        @with_retry(strategy=RetryStrategy(max_attempts=3, initial_delay=0.1))
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_safe_execute(self):
        """Test safe execution."""
        def failing_function():
            raise ValueError("Error")
        
        result = safe_execute(failing_function, fallback_value="fallback")
        self.assertEqual(result, "fallback")


class TestTaskQueue(unittest.TestCase):
    """Test task queue functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.queue = InMemoryTaskQueue()
    
    def test_enqueue_dequeue(self):
        """Test basic enqueue and dequeue."""
        task = Task(
            id="test_1",
            type="test",
            data={"key": "value"},
            priority=TaskPriority.HIGH
        )
        
        self.assertTrue(self.queue.enqueue(task))
        dequeued = self.queue.dequeue()
        
        self.assertIsNotNone(dequeued)
        self.assertEqual(dequeued.id, "test_1")
        self.assertEqual(dequeued.status, TaskStatus.IN_PROGRESS)
    
    def test_priority_ordering(self):
        """Test that tasks are dequeued by priority."""
        low_task = Task(id="low", type="test", data={}, priority=TaskPriority.LOW)
        high_task = Task(id="high", type="test", data={}, priority=TaskPriority.HIGH)
        medium_task = Task(id="medium", type="test", data={}, priority=TaskPriority.MEDIUM)
        
        self.queue.enqueue(low_task)
        self.queue.enqueue(high_task)
        self.queue.enqueue(medium_task)
        
        first = self.queue.dequeue()
        second = self.queue.dequeue()
        third = self.queue.dequeue()
        
        self.assertEqual(first.id, "high")
        self.assertEqual(second.id, "medium")
        self.assertEqual(third.id, "low")
    
    def test_complete_task(self):
        """Test task completion."""
        task = Task(id="test_1", type="test", data={})
        self.queue.enqueue(task)
        
        self.assertTrue(self.queue.complete_task("test_1", result="Done"))
        completed = self.queue.get_task("test_1")
        
        self.assertEqual(completed.status, TaskStatus.COMPLETED)
        self.assertEqual(completed.result, "Done")
    
    def test_fail_and_retry(self):
        """Test task failure and retry logic."""
        task = Task(id="test_1", type="test", data={}, max_retries=2)
        self.queue.enqueue(task)
        self.queue.dequeue()  # Start task
        
        # First failure - should retry
        self.queue.fail_task("test_1", "Error 1")
        failed = self.queue.get_task("test_1")
        self.assertEqual(failed.retry_count, 1)
        self.assertEqual(failed.status, TaskStatus.PENDING)
        
        # Dequeue again
        self.queue.dequeue()
        
        # Second failure - should mark as failed
        self.queue.fail_task("test_1", "Error 2")
        failed = self.queue.get_task("test_1")
        self.assertEqual(failed.retry_count, 2)
        self.assertEqual(failed.status, TaskStatus.FAILED)


class TestAgentHealthMonitoring(unittest.TestCase):
    """Test agent health monitoring."""
    
    def setUp(self):
        """Set up test fixtures."""
        error_handler.error_history.clear()
        error_handler.agent_error_counts.clear()
        error_handler.agent_health_status.clear()
    
    def test_health_degradation(self):
        """Test that agent health degrades with errors."""
        from src.core.error_handler import AgentHealth
        
        agent_id = "test_agent"
        
        # Start healthy
        error_handler.record_success(agent_id)
        health = error_handler.get_agent_health(agent_id)
        self.assertEqual(health, AgentHealth.HEALTHY)
        
        # Add some errors
        for i in range(3):
            error_handler.log_error(
                ValueError(f"Error {i}"),
                f"Context {i}",
                agent_id=agent_id
            )
        
        health = error_handler.get_agent_health(agent_id)
        self.assertEqual(health, AgentHealth.DEGRADED)
        
        # More errors
        for i in range(5):
            error_handler.log_error(
                ValueError(f"Error {i}"),
                f"Context {i}",
                agent_id=agent_id
            )
        
        health = error_handler.get_agent_health(agent_id)
        self.assertIn(health, [AgentHealth.UNHEALTHY, AgentHealth.CRASHED])
    
    def test_should_restart_agent(self):
        """Test restart recommendation."""
        agent_id = "test_agent"
        
        # Healthy agent should not restart
        self.assertFalse(error_handler.should_restart_agent(agent_id))
        
        # Create many errors
        for i in range(15):
            error_handler.log_error(
                ValueError(f"Error {i}"),
                f"Context {i}",
                agent_id=agent_id
            )
        
        # Should recommend restart
        self.assertTrue(error_handler.should_restart_agent(agent_id))


if __name__ == '__main__':
    unittest.main()

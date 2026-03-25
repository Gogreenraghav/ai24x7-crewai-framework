"""
Task Queue Module
Priority-based task queue with status tracking.
Supports both Redis-backed and in-memory implementations.
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from queue import PriorityQueue, Queue, Empty
import threading

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 3
    MEDIUM = 2
    HIGH = 1
    CRITICAL = 0


@dataclass
class Task:
    """Task data structure."""
    id: str
    type: str
    data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = None
    started_at: str = None
    completed_at: str = None
    agent_id: str = None
    result: Any = None
    error: str = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        """Initialize timestamps."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def __lt__(self, other):
        """Compare tasks by priority for priority queue."""
        return self.priority.value < other.priority.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        task_dict = asdict(self)
        task_dict['priority'] = self.priority.name
        task_dict['status'] = self.status.value
        return task_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        if 'priority' in data and isinstance(data['priority'], str):
            data['priority'] = TaskPriority[data['priority']]
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TaskStatus(data['status'])
        return cls(**data)


class InMemoryTaskQueue:
    """In-memory task queue implementation (for MVP/testing)."""
    
    def __init__(self):
        """Initialize in-memory queue."""
        self.queue = PriorityQueue()
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        logger.info("Initialized in-memory task queue")
    
    def enqueue(self, task: Task) -> bool:
        """
        Add task to queue.
        
        Args:
            task: Task to enqueue
            
        Returns:
            True if successful
        """
        with self.lock:
            self.tasks[task.id] = task
            self.queue.put(task)
            logger.info(f"Enqueued task {task.id} with priority {task.priority.name}")
            return True
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Task]:
        """
        Get next task from queue.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            Next task or None if queue is empty
        """
        try:
            task = self.queue.get(timeout=timeout)
            with self.lock:
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.utcnow().isoformat()
                self.tasks[task.id] = task
            logger.info(f"Dequeued task {task.id}")
            return task
        except Empty:
            return None
    
    def update_task(self, task_id: str, **updates) -> bool:
        """
        Update task fields.
        
        Args:
            task_id: Task identifier
            **updates: Fields to update
            
        Returns:
            True if successful
        """
        with self.lock:
            if task_id not in self.tasks:
                logger.warning(f"Task {task_id} not found")
                return False
            
            task = self.tasks[task_id]
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            self.tasks[task_id] = task
            logger.info(f"Updated task {task_id}: {updates}")
            return True
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark task as completed."""
        return self.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow().isoformat(),
            result=result
        )
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark task as failed."""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                # Re-queue for retry
                task.status = TaskStatus.PENDING
                task.started_at = None
                self.queue.put(task)
                logger.info(f"Re-queuing task {task_id} (retry {task.retry_count}/{task.max_retries})")
            else:
                # Max retries reached
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow().isoformat()
                task.error = error
                logger.error(f"Task {task_id} failed after {task.retry_count} retries: {error}")
            
            self.tasks[task_id] = task
            return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with given status."""
        with self.lock:
            return [task for task in self.tasks.values() if task.status == status]
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        with self.lock:
            return list(self.tasks.values())
    
    def get_queue_size(self) -> int:
        """Get number of pending tasks."""
        return self.queue.qsize()
    
    def clear(self):
        """Clear all tasks."""
        with self.lock:
            self.queue = PriorityQueue()
            self.tasks.clear()
            logger.info("Cleared task queue")


class RedisTaskQueue:
    """Redis-backed task queue implementation."""
    
    def __init__(self, redis_url: str = None, prefix: str = "crewai"):
        """
        Initialize Redis task queue.
        
        Args:
            redis_url: Redis connection URL
            prefix: Key prefix for Redis keys
        """
        try:
            import redis
            self.redis_available = True
        except ImportError:
            logger.warning("Redis not available, falling back to in-memory queue")
            self.redis_available = False
            self.fallback = InMemoryTaskQueue()
            return
        
        redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.prefix = prefix
        self.redis = redis.from_url(redis_url, decode_responses=True)
        
        # Redis key patterns
        self.queue_key = f"{prefix}:queue"
        self.tasks_key = f"{prefix}:tasks"
        
        logger.info(f"Initialized Redis task queue at {redis_url}")
    
    def _task_key(self, task_id: str) -> str:
        """Get Redis key for task."""
        return f"{self.tasks_key}:{task_id}"
    
    def enqueue(self, task: Task) -> bool:
        """Add task to Redis queue."""
        if not self.redis_available:
            return self.fallback.enqueue(task)
        
        try:
            # Store task data
            self.redis.set(self._task_key(task.id), json.dumps(task.to_dict()))
            
            # Add to priority queue (using sorted set with priority as score)
            self.redis.zadd(self.queue_key, {task.id: task.priority.value})
            
            logger.info(f"Enqueued task {task.id} to Redis with priority {task.priority.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue task to Redis: {e}")
            return False
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Task]:
        """Get next task from Redis queue."""
        if not self.redis_available:
            return self.fallback.dequeue(timeout)
        
        try:
            # Get highest priority task (lowest score)
            result = self.redis.zpopmin(self.queue_key, 1)
            
            if not result:
                return None
            
            task_id, _ = result[0]
            task_data = self.redis.get(self._task_key(task_id))
            
            if not task_data:
                logger.warning(f"Task {task_id} not found in Redis")
                return None
            
            task = Task.from_dict(json.loads(task_data))
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow().isoformat()
            
            # Update task in Redis
            self.redis.set(self._task_key(task.id), json.dumps(task.to_dict()))
            
            logger.info(f"Dequeued task {task.id} from Redis")
            return task
            
        except Exception as e:
            logger.error(f"Failed to dequeue task from Redis: {e}")
            return None
    
    def update_task(self, task_id: str, **updates) -> bool:
        """Update task in Redis."""
        if not self.redis_available:
            return self.fallback.update_task(task_id, **updates)
        
        try:
            task_data = self.redis.get(self._task_key(task_id))
            if not task_data:
                return False
            
            task = Task.from_dict(json.loads(task_data))
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            self.redis.set(self._task_key(task.id), json.dumps(task.to_dict()))
            logger.info(f"Updated task {task_id} in Redis: {updates}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task in Redis: {e}")
            return False
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark task as completed in Redis."""
        return self.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow().isoformat(),
            result=result
        )
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark task as failed in Redis."""
        if not self.redis_available:
            return self.fallback.fail_task(task_id, error)
        
        try:
            task_data = self.redis.get(self._task_key(task_id))
            if not task_data:
                return False
            
            task = Task.from_dict(json.loads(task_data))
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                # Re-queue for retry
                task.status = TaskStatus.PENDING
                task.started_at = None
                self.redis.set(self._task_key(task.id), json.dumps(task.to_dict()))
                self.redis.zadd(self.queue_key, {task.id: task.priority.value})
                logger.info(f"Re-queued task {task_id} for retry {task.retry_count}/{task.max_retries}")
            else:
                # Max retries reached
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow().isoformat()
                task.error = error
                self.redis.set(self._task_key(task.id), json.dumps(task.to_dict()))
                logger.error(f"Task {task_id} failed after {task.retry_count} retries: {error}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark task as failed in Redis: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID from Redis."""
        if not self.redis_available:
            return self.fallback.get_task(task_id)
        
        try:
            task_data = self.redis.get(self._task_key(task_id))
            if not task_data:
                return None
            return Task.from_dict(json.loads(task_data))
        except Exception as e:
            logger.error(f"Failed to get task from Redis: {e}")
            return None
    
    def get_queue_size(self) -> int:
        """Get number of pending tasks."""
        if not self.redis_available:
            return self.fallback.get_queue_size()
        
        try:
            return self.redis.zcard(self.queue_key)
        except Exception as e:
            logger.error(f"Failed to get queue size from Redis: {e}")
            return 0


# Factory function to create appropriate queue
def create_task_queue(use_redis: bool = None) -> Any:
    """
    Create task queue instance.
    
    Args:
        use_redis: Whether to use Redis (auto-detect if None)
        
    Returns:
        TaskQueue instance
    """
    if use_redis is None:
        use_redis = os.getenv('USE_REDIS', 'false').lower() == 'true'
    
    if use_redis:
        try:
            return RedisTaskQueue()
        except Exception as e:
            logger.warning(f"Failed to initialize Redis queue, using in-memory: {e}")
            return InMemoryTaskQueue()
    else:
        return InMemoryTaskQueue()

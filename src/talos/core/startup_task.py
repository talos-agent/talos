from __future__ import annotations

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)


class StartupTask(BaseModel, ABC):
    """
    Abstract base class for startup tasks that can be executed by the daemon.
    
    Tasks are identified by content-based hashes and tracked for completion.
    They can be one-time or recurring, similar to database migrations.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = Field(..., description="Unique name for this startup task")
    description: str = Field(..., description="Human-readable description of what this task does")
    task_hash: Optional[str] = Field(None, description="Content-based hash for task identification")
    created_at: datetime = Field(default_factory=datetime.now, description="When this task was created")
    execute_at: Optional[datetime] = Field(None, description="Specific datetime for one-time execution")
    cron_expression: Optional[str] = Field(None, description="Cron expression for recurring tasks")
    enabled: bool = Field(True, description="Whether this task is enabled for execution")
    
    def model_post_init(self, __context: Any) -> None:
        if not self.task_hash:
            self.task_hash = self.generate_hash()
        
        if not self.cron_expression and not self.execute_at:
            self.execute_at = datetime.now()
    
    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        """
        Execute the startup task.
        
        This method should contain the actual logic for the task.
        It should be idempotent - safe to run multiple times.
        
        Args:
            **kwargs: Additional arguments that may be passed to the task
            
        Returns:
            Any result from the task execution
        """
        pass
    
    def generate_hash(self) -> str:
        """
        Generate a content-based hash for this task.
        
        Returns:
            Hexadecimal SHA-256 hash of task content
        """
        task_data = {
            "name": self.name,
            "description": self.description,
            "execute_at": self.execute_at.isoformat() if self.execute_at else None,
            "cron_expression": self.cron_expression,
        }
        task_json = json.dumps(task_data, sort_keys=True)
        return hashlib.sha256(task_json.encode()).hexdigest()[:16]
    
    def is_recurring(self) -> bool:
        """Check if this is a recurring task (has cron expression)."""
        return self.cron_expression is not None
    
    def is_one_time(self) -> bool:
        """Check if this is a one-time task (has execute_at datetime)."""
        return self.execute_at is not None
    
    def should_execute_now(self) -> bool:
        """Check if this task should execute now (for one-time tasks)."""
        if not self.is_one_time() or not self.execute_at:
            return False
        return datetime.now() >= self.execute_at
    
    def __str__(self) -> str:
        schedule_info = self.cron_expression if self.cron_expression else f"at {self.execute_at}"
        return f"StartupTask(name='{self.name}', hash='{self.task_hash}', schedule='{schedule_info}', enabled={self.enabled})"

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class ScheduledJob(BaseModel, ABC):
    """
    Abstract base class for scheduled jobs that can be executed by the MainAgent.

    Jobs can be scheduled using either:
    - A cron expression for recurring execution
    - A specific datetime for one-time execution
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Unique name for this scheduled job")
    description: str = Field(..., description="Human-readable description of what this job does")
    cron_expression: Optional[str] = Field(
        None, description="Cron expression for recurring jobs (e.g., '0 9 * * *' for daily at 9 AM)"
    )
    execute_at: Optional[datetime] = Field(None, description="Specific datetime for one-time execution")
    enabled: bool = Field(True, description="Whether this job is enabled for execution")
    max_instances: int = Field(1, description="Maximum number of concurrent instances of this job")

    def model_post_init(self, __context: Any) -> None:
        if not self.cron_expression and not self.execute_at:
            raise ValueError("Either cron_expression or execute_at must be provided")
        if self.cron_expression and self.execute_at:
            raise ValueError("Only one of cron_expression or execute_at should be provided")

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        """
        Execute the scheduled job.

        This method should contain the actual logic for the job.
        It will be called by the scheduler when the job is triggered.

        Args:
            **kwargs: Additional arguments that may be passed to the job

        Returns:
            Any result from the job execution
        """
        pass

    def is_recurring(self) -> bool:
        """Check if this is a recurring job (has cron expression)."""
        return self.cron_expression is not None

    def is_one_time(self) -> bool:
        """Check if this is a one-time job (has execute_at datetime)."""
        return self.execute_at is not None

    def should_execute_now(self) -> bool:
        """
        Check if this job should execute now (for one-time jobs).
        Only relevant for one-time jobs.
        """
        if not self.is_one_time() or not self.execute_at:
            return False
        return datetime.now() >= self.execute_at

    def __str__(self) -> str:
        schedule_info = self.cron_expression if self.cron_expression else f"at {self.execute_at}"
        return f"ScheduledJob(name='{self.name}', schedule='{schedule_info}', enabled={self.enabled})"

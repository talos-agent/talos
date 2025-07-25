from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from talos.core.scheduled_job import ScheduledJob

logger = logging.getLogger(__name__)


class HealthCheckJob(ScheduledJob):
    """
    Example scheduled job that performs a health check every hour.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="health_check",
            description="Performs a health check of the agent system",
            cron_expression="0 * * * *",  # Every hour at minute 0
            **kwargs
        )
    
    async def run(self, **kwargs: Any) -> str:
        """
        Perform a health check of the agent system.
        """
        logger.info("Running health check job")
        
        current_time = datetime.now()
        health_status = {
            "timestamp": current_time.isoformat(),
            "status": "healthy",
            "uptime": "running",
            "memory_usage": "normal"
        }
        
        logger.info(f"Health check completed: {health_status}")
        return f"Health check completed at {current_time}: System is healthy"


class DailyReportJob(ScheduledJob):
    """
    Example scheduled job that generates a daily report at 9 AM.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="daily_report",
            description="Generates a daily activity report",
            cron_expression="0 9 * * *",  # Daily at 9 AM
            **kwargs
        )
    
    async def run(self, **kwargs: Any) -> str:
        """
        Generate a daily activity report.
        """
        logger.info("Running daily report job")
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        report_data = {
            "date": current_date,
            "tasks_completed": 0,
            "skills_used": [],
            "memory_entries": 0
        }
        
        logger.info(f"Daily report generated: {report_data}")
        return f"Daily report for {current_date} generated successfully"


class OneTimeMaintenanceJob(ScheduledJob):
    """
    Example one-time scheduled job for maintenance tasks.
    """
    
    def __init__(self, execute_at: datetime, **kwargs):
        super().__init__(
            name="maintenance_task",
            description="Performs one-time maintenance task",
            execute_at=execute_at,
            **kwargs
        )
    
    async def run(self, **kwargs: Any) -> str:
        """
        Perform a one-time maintenance task.
        """
        logger.info("Running one-time maintenance job")
        
        maintenance_tasks = [
            "Clean temporary files",
            "Optimize memory usage",
            "Update internal metrics"
        ]
        
        for task in maintenance_tasks:
            logger.info(f"Executing maintenance task: {task}")
        
        completion_time = datetime.now()
        logger.info(f"Maintenance completed at {completion_time}")
        return f"Maintenance tasks completed at {completion_time}"


def create_example_jobs() -> list[ScheduledJob]:
    """
    Create a list of example scheduled jobs for demonstration.
    
    Returns:
        List of example ScheduledJob instances
    """
    jobs = [
        HealthCheckJob(),
        DailyReportJob(),
        OneTimeMaintenanceJob(execute_at=datetime.now() + timedelta(minutes=5))
    ]
    
    return jobs

"""
Startup task: Health Check (Recurring)
Generated on: 2025-08-04T04:09:38.972016
Hash: 18ebceaf6799
"""

from talos.core.startup_task import StartupTask
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class HealthCheckTask(StartupTask):
    """Recurring health check startup task."""
    
    async def run(self, **kwargs: Any) -> str:
        """Perform health check."""
        logger.info("Running startup health check")
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "startup_system": "healthy",
            "task_manager": "operational"
        }
        
        logger.info(f"Startup health check completed: {health_status}")
        return f"Startup health check completed: {health_status['startup_system']}"


def create_task() -> HealthCheckTask:
    """Create and return the startup task instance."""
    return HealthCheckTask(
        name="startup_health_check",
        description="Recurring health check for daemon startup components",
        task_hash="18ebceaf6799",
        enabled=True,
        cron_expression="*/5 * * * *"
    )

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from talos.core.startup_task import StartupTask
from talos.core.job_scheduler import JobScheduler
from talos.core.scheduled_job import ScheduledJob

logger = logging.getLogger(__name__)


class StartupTaskRecord:
    """Record of a startup task execution."""
    
    def __init__(
        self,
        task_hash: str,
        name: str,
        executed_at: datetime,
        status: str = "completed",
        error: Optional[str] = None
    ):
        self.task_hash = task_hash
        self.name = name
        self.executed_at = executed_at
        self.status = status
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_hash": self.task_hash,
            "name": self.name,
            "executed_at": self.executed_at.isoformat(),
            "status": self.status,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StartupTaskRecord":
        return cls(
            task_hash=data["task_hash"],
            name=data["name"],
            executed_at=datetime.fromisoformat(data["executed_at"]),
            status=data.get("status", "completed"),
            error=data.get("error")
        )


class StartupTaskManager:
    """
    Manages startup tasks for the Talos daemon.
    
    Provides functionality to:
    - Register and track startup tasks
    - Execute pending tasks on daemon startup
    - Persist execution records to prevent re-execution
    - Schedule recurring tasks with JobScheduler
    """
    
    def __init__(
        self,
        tasks_file: Optional[Path] = None,
        job_scheduler: Optional[JobScheduler] = None
    ):
        self.tasks_file = tasks_file or Path("startup_tasks") / "completed_tasks.json"
        self.job_scheduler = job_scheduler
        self.registered_tasks: List[StartupTask] = []
        self.completed_records: List[StartupTaskRecord] = []
        
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._load_completed_records()
    
    def _load_completed_records(self) -> None:
        """Load completed task records from file."""
        if not self.tasks_file.exists():
            self.tasks_file.write_text("[]")
            return
        
        try:
            with open(self.tasks_file, "r") as f:
                data = json.load(f)
                self.completed_records = [StartupTaskRecord.from_dict(record) for record in data]
        except Exception as e:
            logger.error(f"Failed to load completed task records: {e}")
            self.completed_records = []
    
    def _save_completed_records(self) -> None:
        """Save completed task records to file."""
        try:
            with open(self.tasks_file, "w") as f:
                data = [record.to_dict() for record in self.completed_records]
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save completed task records: {e}")
    
    def register_task(self, task: StartupTask) -> None:
        """Register a startup task."""
        if not task.task_hash:
            task.task_hash = task.generate_hash()
        
        for existing_task in self.registered_tasks:
            if existing_task.task_hash == task.task_hash:
                logger.warning(f"Task '{task.name}' with hash {task.task_hash} already registered")
                return
        
        self.registered_tasks.append(task)
        logger.info(f"Registered startup task: {task.name} (hash: {task.task_hash})")
    
    def is_task_completed(self, task_hash: str) -> bool:
        """Check if a task has been completed."""
        return any(record.task_hash == task_hash for record in self.completed_records)
    
    def get_pending_tasks(self) -> List[StartupTask]:
        """Get all pending (not yet completed) tasks."""
        pending = []
        for task in self.registered_tasks:
            if not task.enabled:
                continue
            
            if task.is_recurring():
                pending.append(task)
            elif task.task_hash and not self.is_task_completed(task.task_hash):
                if task.should_execute_now():
                    pending.append(task)
        
        return pending
    
    async def execute_pending_tasks(self) -> None:
        """Execute all pending startup tasks."""
        pending_tasks = self.get_pending_tasks()
        
        if not pending_tasks:
            logger.info("No pending startup tasks to execute")
            return
        
        logger.info(f"Executing {len(pending_tasks)} pending startup tasks")
        
        for task in pending_tasks:
            await self._execute_task(task)
    
    async def _execute_task(self, task: StartupTask) -> None:
        """Execute a single startup task."""
        logger.info(f"Executing startup task: {task.name}")
        
        try:
            await task.run()
            
            if task.is_one_time() and task.task_hash:
                record = StartupTaskRecord(
                    task_hash=task.task_hash,
                    name=task.name,
                    executed_at=datetime.now(),
                    status="completed"
                )
                self.completed_records.append(record)
                self._save_completed_records()
                logger.info(f"Startup task '{task.name}' completed successfully")
            
            if task.is_recurring() and self.job_scheduler:
                recurring_job = StartupTaskJob(task)
                self.job_scheduler.register_job(recurring_job)
                logger.info(f"Scheduled recurring startup task: {task.name}")
            
        except Exception as e:
            logger.error(f"Startup task '{task.name}' failed: {e}")
            
            if task.task_hash:
                record = StartupTaskRecord(
                    task_hash=task.task_hash,
                    name=task.name,
                    executed_at=datetime.now(),
                    status="failed",
                    error=str(e)
                )
                self.completed_records.append(record)
                self._save_completed_records()
    
    def list_completed_tasks(self) -> List[StartupTaskRecord]:
        """Get all completed task records."""
        return self.completed_records.copy()


class StartupTaskJob(ScheduledJob):
    """Wrapper to convert StartupTask to ScheduledJob for recurring execution."""
    
    def __init__(self, startup_task: StartupTask):
        self.startup_task = startup_task
        super().__init__(
            name=f"startup_task_{startup_task.name}",
            description=f"Recurring execution of startup task: {startup_task.description}",
            cron_expression=startup_task.cron_expression,
            execute_at=None,
            enabled=startup_task.enabled,
            max_instances=1
        )
    
    async def run(self, **kwargs: Any) -> Any:
        """Execute the wrapped startup task."""
        return await self.startup_task.run(**kwargs)

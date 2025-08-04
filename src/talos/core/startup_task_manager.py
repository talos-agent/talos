from __future__ import annotations

import importlib.util
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
    - Discover and load tasks from individual hash-named files
    - Execute pending tasks on daemon startup
    - Persist execution records to prevent re-execution
    - Schedule recurring tasks with JobScheduler
    """
    
    def __init__(
        self,
        tasks_dir: Optional[Path] = None,
        completed_tasks_file: Optional[Path] = None,
        job_scheduler: Optional[JobScheduler] = None
    ):
        self.tasks_dir = tasks_dir or Path("startup_tasks")
        self.completed_tasks_file = completed_tasks_file or self.tasks_dir / "completed_tasks.json"
        self.job_scheduler = job_scheduler
        self.discovered_tasks: List[StartupTask] = []
        self.completed_records: List[StartupTaskRecord] = []
        
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.completed_tasks_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._load_completed_records()
        self._discover_tasks()
    
    def _load_completed_records(self) -> None:
        """Load completed task records from file."""
        if not self.completed_tasks_file.exists():
            self.completed_tasks_file.write_text("[]")
            return
        
        try:
            with open(self.completed_tasks_file, "r") as f:
                data = json.load(f)
                self.completed_records = [StartupTaskRecord.from_dict(record) for record in data]
        except Exception as e:
            logger.error(f"Failed to load completed task records: {e}")
            self.completed_records = []
    
    def _save_completed_records(self) -> None:
        """Save completed task records to file."""
        try:
            with open(self.completed_tasks_file, "w") as f:
                data = [record.to_dict() for record in self.completed_records]
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save completed task records: {e}")
    
    def _discover_tasks(self) -> None:
        """Discover and load startup tasks from individual files."""
        self.discovered_tasks = []
        
        if not self.tasks_dir.exists():
            logger.info("No startup tasks directory found")
            return
        
        task_files = []
        for file_path in self.tasks_dir.glob("*.py"):
            if file_path.name != "__init__.py" and len(file_path.stem) >= 8:
                task_files.append(file_path)
        
        task_files.sort(key=lambda f: f.name)
        
        for task_file in task_files:
            try:
                task = self._load_task_from_file(task_file)
                if task:
                    self.discovered_tasks.append(task)
                    logger.info(f"Discovered startup task: {task.name} from {task_file.name}")
            except Exception as e:
                logger.error(f"Failed to load task from {task_file}: {e}")
        
        logger.info(f"Discovered {len(self.discovered_tasks)} startup tasks")
    
    def _load_task_from_file(self, task_file: Path) -> Optional[StartupTask]:
        """Load a startup task from a Python file."""
        try:
            spec = importlib.util.spec_from_file_location(task_file.stem, task_file)
            if not spec or not spec.loader:
                logger.error(f"Could not load spec for {task_file}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for a function called 'create_task' that returns a StartupTask
            if hasattr(module, 'create_task'):
                task = module.create_task()
                if isinstance(task, StartupTask):
                    if not task.task_hash:
                        task.task_hash = task_file.stem
                    return task
                else:
                    logger.error(f"create_task() in {task_file} did not return a StartupTask instance")
            else:
                logger.error(f"No create_task() function found in {task_file}")
            
        except Exception as e:
            logger.error(f"Error loading task from {task_file}: {e}")
        
        return None
    
    def is_task_completed(self, task_hash: str) -> bool:
        """Check if a task has been completed."""
        return any(record.task_hash == task_hash for record in self.completed_records)
    
    def get_pending_tasks(self) -> List[StartupTask]:
        """Get all pending (not yet completed) tasks."""
        pending = []
        for task in self.discovered_tasks:
            if not task.enabled:
                continue
            
            if task.is_recurring():
                pending.append(task)
            elif task.task_hash and not self.is_task_completed(task.task_hash):
                if task.should_execute_now():
                    pending.append(task)
        
        return pending
    
    def create_task_file(self, task: StartupTask, custom_hash: Optional[str] = None) -> Path:
        """
        Create a new task file with hash-based filename.
        
        Args:
            task: The StartupTask instance to save
            custom_hash: Optional custom hash to use as filename (defaults to task.generate_hash())
        
        Returns:
            Path to the created task file
        """
        if not task.task_hash:
            task.task_hash = task.generate_hash()
        
        filename = custom_hash or task.task_hash
        task_file = self.tasks_dir / f"{filename}.py"
        
        if task_file.exists():
            raise FileExistsError(f"Task file {task_file} already exists")
        
        task_content = self._generate_task_file_content(task)
        
        task_file.write_text(task_content)
        logger.info(f"Created task file: {task_file}")
        
        return task_file
    
    def _generate_task_file_content(self, task: StartupTask) -> str:
        """Generate the content for a task file."""
        task_class_name = task.__class__.__name__
        task_module = task.__class__.__module__
        
        content = f'''"""
Startup task: {task.name}
Generated on: {datetime.now().isoformat()}
Hash: {task.task_hash}
"""

from {task_module} import {task_class_name}


def create_task() -> {task_class_name}:
    """Create and return the startup task instance."""
    return {task_class_name}(
        name="{task.name}",
        description="{task.description}",
        task_hash="{task.task_hash}",
        enabled={task.enabled},
        execute_at={repr(task.execute_at)},
        cron_expression={repr(task.cron_expression)}
    )
'''
        
        return content
    
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

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from talos.core.scheduled_job import ScheduledJob
from talos.hypervisor.supervisor import Supervisor

logger = logging.getLogger(__name__)


class JobScheduler(BaseModel):
    """
    Manages scheduled jobs for the MainAgent using APScheduler.
    
    Provides functionality to:
    - Register and manage scheduled jobs
    - Execute jobs with supervision
    - Handle job lifecycle (start, stop, pause, resume)
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    supervisor: Optional[Supervisor] = Field(None, description="Supervisor for approving job executions")
    timezone: str = Field("UTC", description="Timezone for job scheduling")
    
    _scheduler: AsyncIOScheduler = PrivateAttr()
    _jobs: Dict[str, ScheduledJob] = PrivateAttr(default_factory=dict)
    _running: bool = PrivateAttr(default=False)
    
    def model_post_init(self, __context: Any) -> None:
        self._scheduler = AsyncIOScheduler(timezone=self.timezone)
        self._jobs = {}
        self._running = False
    
    def register_job(self, job: ScheduledJob) -> None:
        """
        Register a scheduled job with the scheduler.
        
        Args:
            job: The ScheduledJob instance to register
        """
        if job.name in self._jobs:
            logger.warning(f"Job '{job.name}' already registered, replacing existing job")
            self.unregister_job(job.name)
        
        self._jobs[job.name] = job
        
        if not job.enabled:
            logger.info(f"Job '{job.name}' registered but disabled")
            return
        
        if job.is_recurring() and job.cron_expression:
            trigger = CronTrigger.from_crontab(job.cron_expression, timezone=self.timezone)
            self._scheduler.add_job(
                func=self._execute_job_with_supervision,
                trigger=trigger,
                args=[job.name],
                id=job.name,
                max_instances=job.max_instances,
                replace_existing=True
            )
            logger.info(f"Registered recurring job '{job.name}' with cron: {job.cron_expression}")
        
        elif job.is_one_time() and job.execute_at:
            trigger = DateTrigger(run_date=job.execute_at, timezone=self.timezone)
            self._scheduler.add_job(
                func=self._execute_job_with_supervision,
                trigger=trigger,
                args=[job.name],
                id=job.name,
                max_instances=job.max_instances,
                replace_existing=True
            )
            logger.info(f"Registered one-time job '{job.name}' for: {job.execute_at}")
    
    def unregister_job(self, job_name: str) -> bool:
        """
        Unregister a scheduled job.
        
        Args:
            job_name: Name of the job to unregister
            
        Returns:
            True if job was found and removed, False otherwise
        """
        if job_name not in self._jobs:
            logger.warning(f"Job '{job_name}' not found for unregistration")
            return False
        
        try:
            self._scheduler.remove_job(job_name)
        except Exception as e:
            logger.warning(f"Failed to remove job '{job_name}' from scheduler: {e}")
        
        del self._jobs[job_name]
        logger.info(f"Unregistered job '{job_name}'")
        return True
    
    def get_job(self, job_name: str) -> Optional[ScheduledJob]:
        """Get a registered job by name."""
        return self._jobs.get(job_name)
    
    def list_jobs(self) -> List[ScheduledJob]:
        """Get all registered jobs."""
        return list(self._jobs.values())
    
    def start(self) -> None:
        """Start the job scheduler."""
        if self._running:
            logger.warning("Job scheduler is already running")
            return
        
        try:
            self._scheduler.start()
            self._running = True
            logger.info("Job scheduler started")
        except RuntimeError as e:
            if "no current event loop" in str(e).lower():
                logger.warning(f"No event loop available for job scheduler: {e}")
                logger.info("Job scheduler will remain inactive (suitable for testing)")
            else:
                logger.error(f"Failed to start job scheduler: {e}")
                raise
    
    def stop(self) -> None:
        """Stop the job scheduler."""
        if not self._running:
            logger.warning("Job scheduler is not running")
            return
        
        self._scheduler.shutdown()
        self._running = False
        logger.info("Job scheduler stopped")
    
    def pause_job(self, job_name: str) -> bool:
        """
        Pause a specific job.
        
        Args:
            job_name: Name of the job to pause
            
        Returns:
            True if job was found and paused, False otherwise
        """
        if not self._running:
            logger.warning("Job scheduler is not running, cannot pause job")
            return False
            
        try:
            self._scheduler.pause_job(job_name)
            logger.info(f"Paused job '{job_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job '{job_name}': {e}")
            return False
    
    def resume_job(self, job_name: str) -> bool:
        """
        Resume a specific job.
        
        Args:
            job_name: Name of the job to resume
            
        Returns:
            True if job was found and resumed, False otherwise
        """
        if not self._running:
            logger.warning("Job scheduler is not running, cannot resume job")
            return False
            
        try:
            self._scheduler.resume_job(job_name)
            logger.info(f"Resumed job '{job_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job '{job_name}': {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._running
    
    async def _execute_job_with_supervision(self, job_name: str) -> None:
        """
        Execute a job with optional supervision.
        
        Args:
            job_name: Name of the job to execute
        """
        job = self._jobs.get(job_name)
        if not job:
            logger.error(f"Job '{job_name}' not found for execution")
            return
        
        if not job.enabled:
            logger.info(f"Job '{job_name}' is disabled, skipping execution")
            return
        
        logger.info(f"Executing scheduled job: {job_name}")
        
        try:
            if self.supervisor:
                logger.info(f"Requesting supervision approval for job: {job_name}")
            
            await job.run()
            logger.info(f"Job '{job_name}' completed successfully")
            
            if job.is_one_time():
                self.unregister_job(job_name)
                logger.info(f"One-time job '{job_name}' removed after execution")
            
        except Exception as e:
            logger.error(f"Job '{job_name}' failed with error: {e}")
            
            if job.is_one_time():
                self.unregister_job(job_name)
                logger.info(f"Failed one-time job '{job_name}' removed")

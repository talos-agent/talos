from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Optional
from unittest.mock import patch

import pytest
from langchain_openai import ChatOpenAI

from talos.core.main_agent import MainAgent
from talos.core.scheduled_job import ScheduledJob
from talos.core.job_scheduler import JobScheduler


class MockScheduledJob(ScheduledJob):
    """Test implementation of ScheduledJob for testing purposes."""
    
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    
    def __init__(self, name: str = "test_job", **kwargs):
        if 'cron_expression' not in kwargs and 'execute_at' not in kwargs:
            kwargs['cron_expression'] = "0 * * * *"  # Every hour
        
        kwargs.setdefault('description', "Test scheduled job")
        kwargs.setdefault('execution_count', 0)
        kwargs.setdefault('last_execution', None)
        
        super().__init__(
            name=name,
            **kwargs
        )
    
    async def run(self, **kwargs) -> str:
        self.execution_count += 1
        self.last_execution = datetime.now()
        return f"Test job executed {self.execution_count} times"


class MockOneTimeJob(ScheduledJob):
    """Test implementation of one-time ScheduledJob."""
    
    executed: bool = False
    
    def __init__(self, execute_at: datetime, **kwargs):
        super().__init__(
            name="one_time_test",
            description="One-time test job",
            execute_at=execute_at,
            executed=False,
            **kwargs
        )
    
    async def run(self, **kwargs) -> str:
        self.executed = True
        return "One-time job executed"


class TestScheduledJobValidation:
    """Test ScheduledJob validation and configuration."""
    
    def test_cron_job_creation(self):
        """Test creating a job with cron expression."""
        job = MockScheduledJob(name="cron_test", cron_expression="0 9 * * *")
        assert job.name == "cron_test"
        assert job.cron_expression == "0 9 * * *"
        assert job.execute_at is None
        assert job.is_recurring()
        assert not job.is_one_time()
    
    def test_one_time_job_creation(self):
        """Test creating a one-time job with datetime."""
        future_time = datetime.now() + timedelta(hours=1)
        job = MockOneTimeJob(execute_at=future_time)
        assert job.name == "one_time_test"
        assert job.execute_at == future_time
        assert job.cron_expression is None
        assert job.is_one_time()
        assert not job.is_recurring()
    
    def test_job_validation_requires_schedule(self):
        """Test that job validation requires either cron or datetime."""
        with pytest.raises(ValueError, match="Either cron_expression or execute_at must be provided"):
            MockScheduledJob(
                name="invalid_job",
                description="Invalid job without schedule",
                cron_expression=None,
                execute_at=None,
                execution_count=0,
                last_execution=None
            )
    
    def test_job_validation_exclusive_schedule(self):
        """Test that job validation prevents both cron and datetime."""
        future_time = datetime.now() + timedelta(hours=1)
        with pytest.raises(ValueError, match="Only one of cron_expression or execute_at should be provided"):
            MockScheduledJob(
                name="invalid_job",
                description="Invalid job with both schedules",
                cron_expression="0 * * * *",
                execute_at=future_time,
                execution_count=0,
                last_execution=None
            )
    
    def test_should_execute_now(self):
        """Test should_execute_now method for one-time jobs."""
        past_time = datetime.now() - timedelta(minutes=1)
        future_time = datetime.now() + timedelta(minutes=1)
        
        past_job = MockOneTimeJob(execute_at=past_time)
        future_job = MockOneTimeJob(execute_at=future_time)
        cron_job = MockScheduledJob()
        
        assert past_job.should_execute_now()
        assert not future_job.should_execute_now()
        assert not cron_job.should_execute_now()


class TestJobScheduler:
    """Test JobScheduler functionality."""
    
    @pytest.fixture
    def scheduler(self):
        """Create a JobScheduler instance for testing."""
        return JobScheduler()
    
    def test_scheduler_initialization(self, scheduler):
        """Test scheduler initialization."""
        assert scheduler.timezone == "UTC"
        assert not scheduler.is_running()
        assert len(scheduler.list_jobs()) == 0
    
    def test_register_job(self, scheduler):
        """Test job registration."""
        job = MockScheduledJob(name="test_register")
        scheduler.register_job(job)
        
        assert len(scheduler.list_jobs()) == 1
        assert scheduler.get_job("test_register") == job
    
    def test_unregister_job(self, scheduler):
        """Test job unregistration."""
        job = MockScheduledJob(name="test_unregister")
        scheduler.register_job(job)
        
        assert scheduler.unregister_job("test_unregister")
        assert len(scheduler.list_jobs()) == 0
        assert scheduler.get_job("test_unregister") is None
    
    def test_unregister_nonexistent_job(self, scheduler):
        """Test unregistering a job that doesn't exist."""
        assert not scheduler.unregister_job("nonexistent")
    
    def test_register_disabled_job(self, scheduler):
        """Test registering a disabled job."""
        job = MockScheduledJob(name="disabled_job", enabled=False)
        scheduler.register_job(job)
        
        assert len(scheduler.list_jobs()) == 1
        assert scheduler.get_job("disabled_job") == job


class TestMainAgentIntegration:
    """Test MainAgent integration with scheduled jobs."""
    
    @pytest.fixture
    def main_agent(self):
        """Create a MainAgent instance for testing."""
        with patch.dict('os.environ', {
            'GITHUB_TOKEN': 'test_token',
            'TWITTER_BEARER_TOKEN': 'test_twitter_token',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            agent = MainAgent(
                model=ChatOpenAI(model="gpt-4o", api_key="test_key"),
                prompts_dir="src/talos/prompts"
            )
            if agent.job_scheduler:
                agent.job_scheduler.stop()
            return agent
    
    def test_main_agent_scheduler_initialization(self, main_agent):
        """Test that MainAgent initializes with a job scheduler."""
        assert main_agent.job_scheduler is not None
        assert isinstance(main_agent.job_scheduler, JobScheduler)
    
    def test_add_scheduled_job(self, main_agent):
        """Test adding a scheduled job to MainAgent."""
        job = MockScheduledJob(name="main_agent_test")
        main_agent.add_scheduled_job(job)
        
        assert len(main_agent.list_scheduled_jobs()) == 1
        assert main_agent.get_scheduled_job("main_agent_test") == job
    
    def test_remove_scheduled_job(self, main_agent):
        """Test removing a scheduled job from MainAgent."""
        job = MockScheduledJob(name="remove_test")
        main_agent.add_scheduled_job(job)
        
        assert main_agent.remove_scheduled_job("remove_test")
        assert len(main_agent.list_scheduled_jobs()) == 0
        assert main_agent.get_scheduled_job("remove_test") is None
    
    def test_pause_resume_job(self, main_agent):
        """Test pausing and resuming jobs."""
        job = MockScheduledJob(name="pause_test")
        main_agent.add_scheduled_job(job)
        
        main_agent.pause_scheduled_job("pause_test")
        main_agent.resume_scheduled_job("pause_test")
    
    def test_predefined_jobs_registration(self):
        """Test that predefined jobs are registered during initialization."""
        job = MockScheduledJob(name="predefined_job")
        
        with patch.dict('os.environ', {
            'GITHUB_TOKEN': 'test_token',
            'TWITTER_BEARER_TOKEN': 'test_twitter_token',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            agent = MainAgent(
                model=ChatOpenAI(model="gpt-4o", api_key="test_key"),
                prompts_dir="src/talos/prompts",
                scheduled_jobs=[job]
            )
            if agent.job_scheduler:
                agent.job_scheduler.stop()
            
            assert len(agent.list_scheduled_jobs()) == 1
            assert agent.get_scheduled_job("predefined_job") == job


def test_job_execution():
    """Test that jobs can be executed."""
    async def run_test():
        job = MockScheduledJob(name="execution_test")
        
        result = await job.run()
        
        assert job.execution_count == 1
        assert job.last_execution is not None
        assert result == "Test job executed 1 times"
        
        result2 = await job.run()
        assert job.execution_count == 2
        assert result2 == "Test job executed 2 times"
    
    asyncio.run(run_test())


def test_one_time_job_execution():
    """Test one-time job execution."""
    async def run_test():
        future_time = datetime.now() + timedelta(seconds=1)
        job = MockOneTimeJob(execute_at=future_time)
        
        assert not job.executed
        
        result = await job.run()
        
        assert job.executed
        assert result == "One-time job executed"
    
    asyncio.run(run_test())

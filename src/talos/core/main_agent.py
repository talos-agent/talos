from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool

from talos.core.agent import Agent
from talos.settings import GitHubSettings
from talos.core.router import Router
from talos.core.scheduled_job import ScheduledJob
from talos.core.job_scheduler import JobScheduler
from talos.hypervisor.hypervisor import Hypervisor
from talos.models.services import Ticket
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.abstract.service import Service
from talos.skills.base import Skill
from talos.skills.cryptography import CryptographySkill
from talos.skills.proposals import ProposalsSkill
from talos.skills.pr_review import PRReviewSkill
from talos.skills.twitter_sentiment import TwitterSentimentSkill
from talos.skills.twitter_influence import TwitterInfluenceSkill
from talos.tools.tool_manager import ToolManager
from talos.tools.github.tools import GithubTools
from talos.tools.document_loader import DocumentLoaderTool, DatasetSearchTool
from talos.data.dataset_manager import DatasetManager


class MainAgent(Agent):
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    Also manages scheduled jobs for autonomous execution.
    """

    router: Optional[Router] = None
    prompts_dir: str
    model: BaseChatModel
    is_main_agent: bool = True
    prompt_manager: Optional[PromptManager] = None
    dataset_manager: Optional[DatasetManager] = None
    job_scheduler: Optional[JobScheduler] = None
    scheduled_jobs: List[ScheduledJob] = []

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._setup_prompt_manager()
        self._setup_router()
        self._setup_hypervisor()
        self._setup_dataset_manager()
        self._setup_tool_manager()
        self._setup_job_scheduler()

    def _setup_prompt_manager(self) -> None:
        if not self.prompt_manager:
            self.prompt_manager = FilePromptManager(self.prompts_dir)
        self.set_prompt(["main_agent_prompt", "general_agent_prompt"])

    def _setup_router(self) -> None:
        github_settings = GitHubSettings()
        github_token = github_settings.GITHUB_TOKEN or github_settings.GITHUB_API_TOKEN
        if not github_token:
            raise ValueError("GITHUB_TOKEN or GITHUB_API_TOKEN environment variable not set.")
        if not self.prompt_manager:
            raise ValueError("Prompt manager not initialized.")
        services: list[Service] = []
        skills: list[Skill] = [
            ProposalsSkill(llm=self.model, prompt_manager=self.prompt_manager),
            TwitterSentimentSkill(prompt_manager=self.prompt_manager),
            CryptographySkill(),
            TwitterInfluenceSkill(llm=self.model, prompt_manager=self.prompt_manager),
            PRReviewSkill(llm=self.model, prompt_manager=self.prompt_manager, github_tools=GithubTools(token=github_token)),
        ]
        if not self.router:
            self.router = Router(services=services, skills=skills)

    def _setup_hypervisor(self) -> None:
        if not self.prompt_manager:
            raise ValueError("Prompt manager not initialized.")
        hypervisor = Hypervisor(
            model=self.model, prompts_dir=self.prompts_dir, prompt_manager=self.prompt_manager, schema=None
        )
        self.add_supervisor(hypervisor)
        hypervisor.register_agent(self)

    def _setup_dataset_manager(self) -> None:
        if not self.dataset_manager:
            self.dataset_manager = DatasetManager()

    def _setup_tool_manager(self) -> None:
        assert self.router is not None
        tool_manager = ToolManager()
        for skill in self.router.skills:
            tool_manager.register_tool(skill.create_ticket_tool())
        tool_manager.register_tool(self._get_ticket_status_tool())
        tool_manager.register_tool(self._add_memory_tool())
        
        if self.dataset_manager:
            tool_manager.register_tool(DocumentLoaderTool(self.dataset_manager))
            tool_manager.register_tool(DatasetSearchTool(self.dataset_manager))
        
        self.tool_manager = tool_manager

    def _setup_job_scheduler(self) -> None:
        """Initialize the job scheduler and register any predefined scheduled jobs."""
        if not self.job_scheduler:
            self.job_scheduler = JobScheduler(supervisor=self.supervisor, timezone="UTC")
        
        for job in self.scheduled_jobs:
            self.job_scheduler.register_job(job)
        
        self.job_scheduler.start()

    def add_scheduled_job(self, job: ScheduledJob) -> None:
        """
        Add a scheduled job to the agent.
        
        Args:
            job: The ScheduledJob instance to add
        """
        if not self.job_scheduler:
            raise ValueError("Job scheduler not initialized")
        
        self.scheduled_jobs.append(job)
        self.job_scheduler.register_job(job)

    def remove_scheduled_job(self, job_name: str) -> bool:
        """
        Remove a scheduled job from the agent.
        
        Args:
            job_name: Name of the job to remove
            
        Returns:
            True if job was found and removed, False otherwise
        """
        if not self.job_scheduler:
            return False
        
        success = self.job_scheduler.unregister_job(job_name)
        
        self.scheduled_jobs = [job for job in self.scheduled_jobs if job.name != job_name]
        
        return success

    def list_scheduled_jobs(self) -> List[ScheduledJob]:
        """Get all scheduled jobs."""
        return self.scheduled_jobs.copy()

    def get_scheduled_job(self, job_name: str) -> Optional[ScheduledJob]:
        """Get a scheduled job by name."""
        if not self.job_scheduler:
            return None
        return self.job_scheduler.get_job(job_name)

    def pause_scheduled_job(self, job_name: str) -> bool:
        """Pause a scheduled job."""
        if not self.job_scheduler:
            return False
        return self.job_scheduler.pause_job(job_name)

    def resume_scheduled_job(self, job_name: str) -> bool:
        """Resume a scheduled job."""
        if not self.job_scheduler:
            return False
        return self.job_scheduler.resume_job(job_name)

    def _add_memory_tool(self) -> BaseTool:
        @tool
        def add_memory(description: str, metadata: Optional[dict] = None) -> str:
            """
            Adds a memory to the agent's long-term memory.

            Args:
                description: A description of the memory to add.
                metadata: Optional metadata to associate with the memory.

            Returns:
                A confirmation message.
            """
            if self.memory:
                self.memory.add_memory(description, metadata)
                return "Memory added successfully."
            return "Memory not configured for this agent."

        return add_memory

    def _get_ticket_status_tool(self) -> BaseTool:
        @tool
        def get_ticket_status(service_name: str, ticket_id: str) -> Ticket:
            """
            Get the status of a ticket.

            Args:
                service_name: The name of the service that the ticket was created for.
                ticket_id: The ID of the ticket.

            Returns:
                The ticket object.
            """
            assert self.router is not None
            skill = self.router.get_skill(service_name)
            if not skill:
                raise ValueError(f"Skill '{service_name}' not found.")
            ticket = skill.get_ticket_status(ticket_id)
            if not ticket:
                raise ValueError(f"Ticket '{ticket_id}' not found.")
            return ticket

        return get_ticket_status

    def _build_context(self, query: str, **kwargs) -> dict:
        assert self.router is not None
        
        base_context = super()._build_context(query, **kwargs)
        
        active_tickets = self.router.get_all_tickets()
        ticket_info = [f"- {ticket.ticket_id}: last updated at {ticket.updated_at}" for ticket in active_tickets]
        
        main_agent_context = {
            "time": datetime.now().isoformat(),
            "available_services": ", ".join([service.name for service in self.router.services]),
            "active_tickets": " ".join(ticket_info),
        }
        
        return {**base_context, **main_agent_context}

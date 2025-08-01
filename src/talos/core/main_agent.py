from __future__ import annotations

import os
from datetime import datetime
from typing import Any, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool

from talos.core.agent import Agent
from talos.core.job_scheduler import JobScheduler
from talos.core.scheduled_job import ScheduledJob
from talos.data.dataset_manager import DatasetManager
from talos.hypervisor.hypervisor import Hypervisor
from talos.models.services import Ticket
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.abstract.service import Service
from talos.settings import GitHubSettings
from talos.skills.base import Skill
from talos.skills.codebase_evaluation import CodebaseEvaluationSkill
from talos.skills.cryptography import CryptographySkill
from talos.skills.pr_review import PRReviewSkill
from talos.skills.proposals import ProposalsSkill
from talos.skills.twitter_influence import TwitterInfluenceSkill
from talos.skills.twitter_sentiment import TwitterSentimentSkill
from talos.tools.arbiscan import ArbiScanABITool, ArbiScanSourceCodeTool
from talos.tools.document_loader import DatasetSearchTool, DocumentLoaderTool
from talos.tools.github.tools import GithubTools
from talos.tools.tool_manager import ToolManager


class MainAgent(Agent):
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    Also manages scheduled jobs for autonomous execution.
    """

    skills: list[Skill] = []
    services: list[Service] = []
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
        self._ensure_user_id()
        self._setup_memory()
        self._setup_skills_and_services()
        self._setup_hypervisor()
        self._setup_dataset_manager()
        self._setup_tool_manager()
        self._setup_job_scheduler()
        
    def _get_verbose_level(self) -> int:
        """Convert verbose to integer level for backward compatibility."""
        if isinstance(self.verbose, bool):
            return 1 if self.verbose else 0
        return max(0, min(2, self.verbose))

    def _setup_prompt_manager(self) -> None:
        if not self.prompt_manager:
            self.prompt_manager = FilePromptManager(self.prompts_dir)
        
        use_voice_enhanced = os.getenv("TALOS_USE_VOICE_ENHANCED", "false").lower() == "true"
        
        if use_voice_enhanced:
            self._setup_voice_enhanced_prompt()
        else:
            self.set_prompt(["main_agent_prompt", "general_agent_prompt"])

    def _setup_voice_enhanced_prompt(self) -> None:
        """Setup voice-enhanced prompt by combining voice analysis with main prompt."""
        try:
            if not self.prompt_manager:
                raise ValueError("Prompt manager not initialized")
                
            from talos.skills.twitter_voice import TwitterVoiceSkill
            
            voice_skill = TwitterVoiceSkill()
            voice_result = voice_skill.run(username="talos_is")
            
            main_prompt = self.prompt_manager.get_prompt("main_agent_prompt")
            if not main_prompt:
                raise ValueError("Could not find main_agent_prompt")
            
            voice_enhanced_template = f"{voice_result['voice_prompt']}\n\n{main_prompt.template}"
            
            from talos.prompts.prompt import Prompt
            enhanced_prompt = Prompt(
                name="voice_enhanced_main_agent",
                template=voice_enhanced_template,
                input_variables=main_prompt.input_variables
            )
            
            # Add the enhanced prompt to the manager if it's a FilePromptManager
            if hasattr(self.prompt_manager, 'prompts'):
                self.prompt_manager.prompts["voice_enhanced_main_agent"] = enhanced_prompt
            
            self.set_prompt(["voice_enhanced_main_agent", "general_agent_prompt"])
            
            if self._get_verbose_level() >= 1:
                print(f"Voice integration enabled using {voice_result['voice_source']}")
                
        except Exception as e:
            if self._get_verbose_level() >= 1:
                print(f"Voice integration failed, falling back to default prompts: {e}")
            self.set_prompt(["main_agent_prompt", "general_agent_prompt"])

    def _ensure_user_id(self) -> None:
        """Ensure user_id is set, generate temporary one if needed."""
        if not self.user_id and self.use_database_memory:
            import uuid

            self.user_id = str(uuid.uuid4())

    def _setup_memory(self) -> None:
        """Initialize memory with database or file backend based on configuration."""
        if not self.memory:
            from langchain_openai import OpenAIEmbeddings

            from talos.core.memory import Memory

            embeddings_model = OpenAIEmbeddings()

            if self.use_database_memory:
                from talos.database.session import init_database

                init_database()

                session_id = self.session_id or "cli-session"

                self.memory = Memory(
                    embeddings_model=embeddings_model,
                    user_id=self.user_id,
                    session_id=session_id,
                    use_database=True,
                    auto_save=True,
                    verbose=self.verbose,
                )
            else:
                from pathlib import Path

                memory_dir = Path("memory")
                memory_dir.mkdir(exist_ok=True)

                self.memory = Memory(
                    file_path=memory_dir / "memories.json",
                    embeddings_model=embeddings_model,
                    history_file_path=memory_dir / "history.json",
                    use_database=False,
                    auto_save=True,
                    verbose=self.verbose,
                )

    def _setup_skills_and_services(self) -> None:
        if not self.prompt_manager:
            raise ValueError("Prompt manager not initialized.")
        services: list[Service] = []
        skills: list[Skill] = [
            ProposalsSkill(llm=self.model, prompt_manager=self.prompt_manager),
            CryptographySkill(),
            CodebaseEvaluationSkill(llm=self.model, prompt_manager=self.prompt_manager),
        ]

        try:
            import os

            from talos.services.implementations.devin import DevinService

            devin_api_key = os.getenv("DEVIN_API_KEY")
            if devin_api_key:
                services.append(DevinService(api_key=devin_api_key))
        except (ImportError, ValueError):
            pass  # Devin API key not available, skip Devin service

        try:
            github_settings = GitHubSettings()
            github_token = github_settings.GITHUB_API_TOKEN
            if github_token:
                skills.append(
                    PRReviewSkill(
                        llm=self.model, prompt_manager=self.prompt_manager, github_tools=GithubTools(token=github_token)
                    )
                )
        except ValueError:
            pass  # GitHub token not available, skip GitHub-dependent skills

        try:
            from talos.tools.twitter_client import TwitterConfig

            TwitterConfig()  # This will raise ValueError if TWITTER_BEARER_TOKEN is not set
            skills.extend(
                [
                    TwitterSentimentSkill(prompt_manager=self.prompt_manager),
                    TwitterInfluenceSkill(llm=self.model, prompt_manager=self.prompt_manager),
                ]
            )
        except ValueError:
            pass  # Twitter token not available, skip Twitter-dependent skills

        self.skills = skills
        self.services = services

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
            if self.use_database_memory:
                from talos.database.session import init_database
                init_database()
                
                self.dataset_manager = DatasetManager(
                    verbose=self.verbose,
                    user_id=self.user_id,
                    session_id=self.session_id or "cli-session",
                    use_database=True
                )
            else:
                self.dataset_manager = DatasetManager(verbose=self.verbose)

    def _setup_tool_manager(self) -> None:
        tool_manager = ToolManager()
        for skill in self.skills:
            tool_manager.register_tool(skill.create_ticket_tool())
        tool_manager.register_tool(self._get_ticket_status_tool())
        tool_manager.register_tool(self._add_memory_tool())

        if self.dataset_manager:
            tool_manager.register_tool(DocumentLoaderTool(self.dataset_manager))
            tool_manager.register_tool(DatasetSearchTool(self.dataset_manager))

        tool_manager.register_tool(ArbiScanSourceCodeTool())
        tool_manager.register_tool(ArbiScanABITool())

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
                return f"Added to memory: {description}"
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
            skill = None
            for s in self.skills:
                if s.name == service_name:
                    skill = s
                    break
            if not skill:
                raise ValueError(f"Skill '{service_name}' not found.")
            ticket = skill.get_ticket_status(ticket_id)
            if not ticket:
                raise ValueError(f"Ticket '{ticket_id}' not found.")
            return ticket

        return get_ticket_status

    def _build_context(self, query: str, **kwargs) -> dict:
        base_context = super()._build_context(query, **kwargs)

        active_tickets = []
        for skill in self.skills:
            active_tickets.extend(skill.get_all_tickets())
        ticket_info = [f"- {ticket.ticket_id}: last updated at {ticket.updated_at}" for ticket in active_tickets]

        main_agent_context = {
            "time": datetime.now().isoformat(),
            "available_services": ", ".join([service.name for service in self.services]),
            "active_tickets": " ".join(ticket_info),
        }

        return {**base_context, **main_agent_context}

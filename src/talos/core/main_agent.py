from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool

from talos.core.agent import Agent
from talos.core.router import Router
from talos.hypervisor.hypervisor import Hypervisor
from talos.models.services import Ticket
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.abstract.service import Service
from talos.skills.base import Skill
from talos.skills.cryptography import CryptographySkill
from talos.skills.proposals import ProposalsSkill
from talos.skills.twitter import TwitterSkill
from talos.tools.tool_manager import ToolManager


class MainAgent(Agent):
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    """

    router: Optional[Router] = None
    prompts_dir: str
    model: BaseChatModel
    is_main_agent: bool = True
    prompt_manager: Optional[PromptManager] = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._setup_prompt_manager()
        self._setup_router()
        self._setup_hypervisor()
        self._setup_tool_manager()

    def _setup_prompt_manager(self) -> None:
        if not self.prompt_manager:
            self.prompt_manager = FilePromptManager(self.prompts_dir)
        self.set_prompt(["main_agent_prompt", "general_agent_prompt"])

    def _setup_router(self) -> None:
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable not set.")
        if not self.prompt_manager:
            raise ValueError("Prompt manager not initialized.")
        services: list[Service] = []
        skills: list[Skill] = [
            ProposalsSkill(llm=self.model, prompt_manager=self.prompt_manager),
            TwitterSkill(),
            CryptographySkill(),
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

    def _setup_tool_manager(self) -> None:
        assert self.router is not None
        tool_manager = ToolManager()
        for skill in self.router.skills:
            tool_manager.register_tool(skill.create_ticket_tool())
        tool_manager.register_tool(self._get_ticket_status_tool())
        tool_manager.register_tool(self._add_memory_tool())
        self.tool_manager = tool_manager

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
        active_tickets = self.router.get_all_tickets()
        ticket_info = [f"- {ticket.ticket_id}: last updated at {ticket.updated_at}" for ticket in active_tickets]
        return {
            "time": datetime.now().isoformat(),
            "available_services": ", ".join([service.name for service in self.router.services]),
            "active_tickets": " ".join(ticket_info),
        }

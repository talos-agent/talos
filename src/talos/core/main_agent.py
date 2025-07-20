from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from talos.core.agent import Agent
from talos.core.router import Router
from talos.hypervisor.hypervisor import Hypervisor
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.base import Service
from talos.services.implementations import GitHubService, ProposalsService, TwitterService
from talos.services.models import Ticket
from talos.tools.tool_manager import ToolManager


class MainAgent(Agent):
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    """

    router: Optional[Router] = None
    prompts_dir: str
    model: BaseChatModel
    is_main_agent: bool = True
    prompt_manager: Optional[PromptManager] = None  # type: ignore

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if not self.prompt_manager:
            self.prompt_manager = FilePromptManager(self.prompts_dir)
        self.set_prompt("main_agent_prompt")
        services: list[Service] = [
            ProposalsService(llm=self.model, prompt_manager=self.prompt_manager),
            TwitterService(),
            GitHubService(llm=self.model, token=os.environ.get("GITHUB_TOKEN")),
        ]
        if not self.router:
            self.router = Router(services)
        hypervisor = Hypervisor(
            model=self.model, prompts_dir=self.prompts_dir, prompt_manager=self.prompt_manager, schema=None
        )
        tool_manager = ToolManager()
        for service in services:
            tool_manager.register_tool(service.create_ticket_tool())

        tool_manager.register_tool(self.get_ticket_status_tool())
        self.tool_manager = tool_manager
        self.add_supervisor(hypervisor)

    def get_ticket_status_tool(self):
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
            service = self.router.get_service(service_name)
            if not service:
                raise ValueError(f"Service '{service_name}' not found.")
            ticket = service.get_ticket_status(ticket_id)
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

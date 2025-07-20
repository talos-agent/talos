from __future__ import annotations

import os
from datetime import datetime

from langchain_core.language_models import BaseChatModel

from talos.core.agent import Agent
from talos.core.router import Router
from talos.hypervisor.hypervisor import Hypervisor
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.base import Service
from talos.services.implementations import (
    GitHubService,
    ProposalsService,
    TwitterService,
)
from talos.services.models import Ticket
from talos.tools.tool_manager import ToolManager


class MainAgent(Agent):
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        prompts_dir: str,
    ):
        services: list[Service] = [
            ProposalsService(llm=llm),
            TwitterService(),
            GitHubService(llm=llm, token=os.environ.get("GITHUB_TOKEN")),
        ]
        self.router = Router(services)
        self.prompt_manager = FilePromptManager(prompts_dir)
        hypervisor = Hypervisor(llm=llm, prompts_dir=prompts_dir)
        tool_manager = ToolManager()
        for service in services:
            tool_manager.register_tool(service.create_ticket_tool())

        tool_manager.register_tool(self.get_ticket_status_tool())
        super().__init__(
            model=llm,
            prompt_manager=self.prompt_manager,
            tool_manager=tool_manager,
        )
        self.add_supervisor(hypervisor)

    def get_ticket_status_tool(self):
        def get_ticket_status(service_name: str, ticket_id: str) -> Ticket:
            """
            Get the status of a ticket.

            Args:
                service_name: The name of the service that the ticket was created for.
                ticket_id: The ID of the ticket.

            Returns:
                The ticket object.
            """
            service = self.router.get_service(service_name)
            if not service:
                raise ValueError(f"Service '{service_name}' not found.")
            ticket = service.get_ticket_status(ticket_id)
            if not ticket:
                raise ValueError(f"Ticket '{ticket_id}' not found.")
            return ticket

        return get_ticket_status

    def _add_context(self, query: str, **kwargs) -> str:
        active_tickets = self.router.get_all_tickets()
        ticket_info = [
            f"- {ticket.ticket_id}: last updated at {ticket.updated_at}"
            for ticket in active_tickets
        ]
        return (
            f"It is currently {datetime.now().isoformat()}. You have the following services available: "
            f"{', '.join([service.name for service in self.router.services])}. "
            f"You have the following active tickets:\n{' '.join(ticket_info)}\n\n"
            f"What would you like to do? Keep in mind that you can only interact with the user and "
            f"the available services. You can also create new tickets to delegate tasks to other agents."
        )

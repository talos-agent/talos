from __future__ import annotations

import os
from datetime import datetime

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

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
from talos.services.models import TicketCreationRequest
from talos.services.proposals.models import Proposal, QueryResponse, RunParams
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
            GitHubService(llm=llm, token=os.environ.get("GITHUB_TOKEN", "")),
        ]
        self.router = Router(services)
        self.prompt_manager = FilePromptManager(prompts_dir)
        self.hypervisor = Hypervisor()
        super().__init__(
            model=llm,
            prompt_manager=self.prompt_manager,
            tool_manager=ToolManager(),
        )

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

    def run(self, message: str, history: list[BaseMessage] | None = None, **kwargs) -> BaseModel:  # type: ignore
        params = RunParams.model_validate(kwargs)
        if params.tool and params.tool in self.tool_manager.get_all_tools():
            return self.run_tool(params.tool, params.tool_args or {})  # type: ignore
        elif params.prompt and self.prompt_manager.get_prompt(params.prompt):
            return self.run_prompt(params.prompt, params.prompt_args or {})  # type: ignore
        else:
            service = self.router.route(message)
            if service:
                request = TicketCreationRequest(
                    tool=service.name,
                    tool_args=params.model_dump(),
                )
                ticket = service.create_ticket(request)
                return QueryResponse(answers=[f"Ticket created: {ticket.ticket_id}"])
            return super().run(message, history, **kwargs)


    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
        """
        Evaluates a proposal.
        """
        proposals_service = self.router.get_service("proposals")
        if proposals_service and isinstance(proposals_service, ProposalsService):
            result = proposals_service.evaluate_proposal(proposal, feedback=[])
            return QueryResponse(answers=result.answers)
        else:
            return QueryResponse(answers=["Proposals service not loaded"])

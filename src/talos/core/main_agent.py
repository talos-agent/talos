import os

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool as Tool

from talos.core.router import Router
from talos.hypervisor.hypervisor import Hypervisor
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.base import Service
from talos.services.implementations import (
    GitHubService,
    ProposalsService,
    TwitterService,
)
from talos.services.models import QueryResponse, RunParams, TicketCreationRequest
from talos.services.proposals.models import Proposal


class MainAgent:
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        tools: "list[Tool]",
        prompts_dir: str,
    ):
        self.services: dict[str, Service] = {}
        self.services["proposals"] = ProposalsService(llm=llm)
        self.services["twitter"] = TwitterService()
        self.services["github"] = GitHubService(
            llm=llm, token=os.environ.get("GITHUB_TOKEN", "")
        )
        self.tools = {tool.name: tool for tool in tools}
        self.prompt_manager = FilePromptManager(prompts_dir)
        self.history: "list[dict[str, str]]" = []
        self.hypervisor = Hypervisor()
        self.router = Router(list(self.services.values()))

    def add_to_history(self, user_message: str, agent_response: str) -> None:
        """
        Adds a message to the conversation history.
        """
        self.history.append({"user": user_message, "agent": agent_response})

    def pop_from_history(self) -> "dict[str, str]":
        """
        Pops the last message from the conversation history.
        """
        return self.history.pop()

    def reset_history(self) -> None:
        """
        Resets the conversation history.
        """
        self.history = []

    def run(self, query: str, params: RunParams) -> QueryResponse:
        """
        Runs the appropriate agent based on the query and parameters.
        """
        # This is a temporary way to route to the correct discipline.
        # A more sophisticated routing mechanism will be needed in the future.
        if params.tool and params.tool in self.tools:
            return self.run_tool(params.tool, params.tool_args or {})
        elif params.prompt and params.prompt in self.prompt_manager.prompts:
            return self.run_prompt(params.prompt, params.prompt_args or {})
        else:
            service = self.router.route(query)
            if service:
                # This is a temporary way to create a ticket.
                # A more sophisticated ticket creation mechanism will be needed in the future.
                request = TicketCreationRequest(
                    tool=service.name,
                    tool_args=params.model_dump(),
                )
                ticket = service.create_ticket(request)
                return QueryResponse(answers=[f"Ticket created: {ticket.ticket_id}"])
            return QueryResponse(answers=["No service found for your query"])

    def run_tool(self, tool_name: str, tool_args: dict) -> QueryResponse:
        """
        Runs a tool.
        """
        if self.hypervisor.approve("run_tool", {"tool_name": tool_name, "tool_args": tool_args}):
            tool = self.tools.get(tool_name)
            if tool:
                result = tool.run(**tool_args)
                return QueryResponse(answers=[result])
            else:
                return QueryResponse(answers=[f"Tool {tool_name} not found"])
        else:
            return QueryResponse(answers=["Action denied by hypervisor"])

    def run_prompt(self, prompt_name: str, prompt_args: dict) -> QueryResponse:
        """
        Runs a prompt.
        """
        if self.hypervisor.approve("run_prompt", {"prompt_name": prompt_name, "prompt_args": prompt_args}):
            prompt = self.prompt_manager.get_prompt(prompt_name)
            if prompt:
                result = prompt.format(**prompt_args)
                return QueryResponse(answers=[result])
            else:
                return QueryResponse(answers=[f"Prompt {prompt_name} not found"])
        else:
            return QueryResponse(answers=["Action denied by hypervisor"])

    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
        """
        Evaluates a proposal.
        """
        proposals_service = self.services.get("proposals")
        if proposals_service and isinstance(proposals_service, ProposalsService):
            return proposals_service.evaluate_proposal(proposal, feedback=[])
        else:
            return QueryResponse(answers=["Proposals service not loaded"])

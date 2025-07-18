from typing import Dict, List
from talos.disciplines.base import Discipline
from talos.disciplines.implementations import (
    ProposalsDiscipline,
    TwitterDiscipline,
    GitHubDiscipline,
    OnChainManagementDiscipline,
    GitBookDiscipline,
)
from talos.disciplines.proposals.models import Proposal, QueryResponse, RunParams
from talos.tools.basetool import Tool
from talos.prompts.prompt_manager import PromptManager
from talos.hypervisor.hypervisor import Hypervisor
from langchain_openai import OpenAI


class MainAgent:
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    """

    def __init__(
        self,
        openai_api_key: str,
        tools: List[Tool],
        prompts_dir: str,
        model: str = "text-davinci-003",
    ):
        llm = OpenAI(model_name=model, openai_api_key=openai_api_key)
        self.disciplines: Dict[str, Discipline] = {
            "proposals": ProposalsDiscipline(llm=llm),
            "twitter": TwitterDiscipline(),
            "github": GitHubDiscipline(),
            "onchain": OnChainManagementDiscipline(),
            "gitbook": GitBookDiscipline(),
        }
        self.tools = {tool.name: tool for tool in tools}
        self.prompt_manager = PromptManager(prompts_dir)
        self.history: List[Dict[str, str]] = []
        self.hypervisor = Hypervisor()

    def add_to_history(self, user_message: str, agent_response: str) -> None:
        """
        Adds a message to the conversation history.
        """
        self.history.append({"user": user_message, "agent": agent_response})

    def pop_from_history(self) -> Dict[str, str]:
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
        if params.tool in self.tools:
            return self.run_tool(params.tool, params.tool_args)
        elif params.prompt in self.prompt_manager.prompts:
            return self.run_prompt(params.prompt, params.prompt_args)
        elif params.discipline in self.disciplines:
            discipline = self.disciplines[params.discipline]
            # This is a placeholder for actually calling the discipline
            return QueryResponse(answers=[{"answer": f"Using {discipline.name} discipline", "score": 1.0}])
        else:
            return QueryResponse(answers=[{"answer": "No discipline specified", "score": 1.0}])

    def run_tool(self, tool_name: str, tool_args: dict) -> QueryResponse:
        """
        Runs a tool.
        """
        if self.hypervisor.approve("run_tool", {"tool_name": tool_name, "tool_args": tool_args}):
            tool = self.tools.get(tool_name)
            if tool:
                result = tool.run(**tool_args)
                return QueryResponse(answers=[{"answer": result, "score": 1.0}])
            else:
                return QueryResponse(answers=[{"answer": f"Tool {tool_name} not found", "score": 0.0}])
        else:
            return QueryResponse(answers=[{"answer": "Action denied by hypervisor", "score": 0.0}])

    def run_prompt(self, prompt_name: str, prompt_args: dict) -> QueryResponse:
        """
        Runs a prompt.
        """
        if self.hypervisor.approve("run_prompt", {"prompt_name": prompt_name, "prompt_args": prompt_args}):
            prompt = self.prompt_manager.get_prompt(prompt_name)
            if prompt:
                result = prompt.format(**prompt_args)
                return QueryResponse(answers=[{"answer": result, "score": 1.0}])
            else:
                return QueryResponse(answers=[{"answer": f"Prompt {prompt_name} not found", "score": 0.0}])
        else:
            return QueryResponse(answers=[{"answer": "Action denied by hypervisor", "score": 0.0}])

    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
        """
        Evaluates a proposal.
        """
        proposals_discipline = self.disciplines.get("proposals")
        if proposals_discipline:
            return proposals_discipline.evaluate_proposal(proposal)
        else:
            return QueryResponse(answers=[{"answer": "Proposals discipline not loaded", "score": 0.0}])

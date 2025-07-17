from typing import Dict, List
from src.disciplines.base import Discipline
from src.disciplines.implementations import *
from src.disciplines.proposals.models import Proposal, QueryResponse, RunParams
from src.tools.base import Tool


class MainAgent:
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    """

    def __init__(
        self,
        openai_api_key: str,
        tools: List[Tool],
    ):
        self.disciplines: Dict[str, Discipline] = {
            "proposals": ProposalsDiscipline(openai_api_key=openai_api_key),
            "twitter": TwitterDiscipline(),
            "github": GitHubDiscipline(),
            "onchain": OnChainManagementDiscipline(),
            "gitbook": GitBookDiscipline(),
        }
        self.tools = {tool.name: tool for tool in tools}

    def run(self, query: str, params: RunParams) -> QueryResponse:
        """
        Runs the appropriate agent based on the query and parameters.
        """
        # This is a temporary way to route to the correct discipline.
        # A more sophisticated routing mechanism will be needed in the future.
        if params.tool in self.tools:
            return self.run_tool(params.tool, params.tool_args)
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
        tool = self.tools.get(tool_name)
        if tool:
            result = tool.run(**tool_args)
            return QueryResponse(answers=[{"answer": result, "score": 1.0}])
        else:
            return QueryResponse(answers=[{"answer": f"Tool {tool_name} not found", "score": 0.0}])

    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
        """
        Evaluates a proposal.
        """
        proposals_discipline = self.disciplines.get("proposals")
        if proposals_discipline:
            return proposals_discipline.evaluate_proposal(proposal)
        else:
            return QueryResponse(answers=[{"answer": "Proposals discipline not loaded", "score": 0.0}])

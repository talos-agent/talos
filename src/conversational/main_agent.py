from typing import Optional

from conversational.letta_agent import LettaAgent
from research.haystack_agent import HaystackAgent
from research.models import AddDatasetParams, QueryResponse, RunParams


class MainAgent:
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    """

    def __init__(self, letta_api_key: str, letta_agent_id: str):
        self.conversational_agent = LettaAgent(
            api_key=letta_api_key, agent_id=letta_agent_id
        )
        self.research_agent = HaystackAgent()

    def run(self, query: str, params: RunParams) -> QueryResponse:
        """
        Runs the appropriate agent based on the query and parameters.
        """
        if params.web_search or "research" in query.lower():
            return self.research_agent.run(query, params)
        else:
            return self.conversational_agent.run(query, params)

    def add_dataset(self, dataset_path: str, params: AddDatasetParams) -> None:
        """
        Adds a dataset to the research agent.
        """
        self.research_agent.add_dataset(dataset_path, params)

from typing import Optional

import letta
from letta.sdk import LettaSDK

from research.abc import Agent
from research.models import AddDatasetParams, QueryResponse, RunParams


class LettaAgent(Agent):
    """
    A Letta-based agent for managing conversational memory.
    """

    def __init__(self, api_key: str, agent_id: str):
        self.sdk = LettaSDK(api_key=api_key)
        self.agent_id = agent_id

    def run(self, query: str, params: RunParams) -> QueryResponse:
        """
        Sends a message to the Letta agent and returns the response.
        """
        response = self.sdk.agents.messages.create(
            agent_id=self.agent_id,
            content=query,
            stream=False,
        )
        return QueryResponse(answers=[{"answer": response.content, "score": 1.0}])

    def add_dataset(self, dataset_path: str, params: AddDatasetParams) -> None:
        """
        This method is not applicable to the Letta agent.
        """
        raise NotImplementedError("The Letta agent does not support adding datasets directly.")

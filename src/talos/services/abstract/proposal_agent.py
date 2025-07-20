from abc import abstractmethod
from typing import Any

from talos.services.base import Service
from talos.services.proposals.models import QueryResponse


class ProposalAgent(Service):
    """
    An abstract base class for an agent that can evaluate proposals.
    """

    def __init__(self, rag_dataset: Any, tools: list[Any]):
        self.rag_dataset = rag_dataset
        self.tools = tools

    @property
    def name(self) -> str:
        return "proposals"

    @abstractmethod
    def evaluate_proposal(
        self, proposal: "Proposal", feedback: list[dict[str, Any]]
    ) -> QueryResponse:
        """
        Evaluates a proposal and returns a recommendation.

        :param proposal: The proposal to evaluate.
        :param feedback: A list of feedback from delegates.
        :return: The agent's recommendation.
        """
        from talos.services.proposals.models import Proposal
        pass

from abc import ABC, abstractmethod

from research.models import Proposal, QueryResponse


class ProposalAgent(ABC):
    """
    An abstract base class for an agent that can evaluate proposals.
    """

    @abstractmethod
    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
        """
        Evaluates a proposal and returns a recommendation.

        :param proposal: The proposal to evaluate.
        :return: The agent's recommendation.
        """
        pass

from abc import abstractmethod

from disciplines.base import Discipline
from research.models import Proposal, QueryResponse


class ProposalAgent(Discipline):
    """
    An abstract base class for an agent that can evaluate proposals.
    """

    @property
    def name(self) -> str:
        return "proposals"

    @abstractmethod
    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
        """
        Evaluates a proposal and returns a recommendation.

        :param proposal: The proposal to evaluate.
        :return: The agent's recommendation.
        """
        pass

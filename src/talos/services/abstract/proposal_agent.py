from __future__ import annotations

from abc import abstractmethod
from typing import Any

from talos.models.proposals import Proposal, ProposalResponse
from talos.services.abstract.service import Service


class ProposalAgent(Service):
    """
    An abstract base class for an agent that can evaluate proposals.
    """

    rag_dataset: Any | None = None
    tools: list[Any] | None = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

    @property
    def name(self) -> str:
        return "proposals"

    @abstractmethod
    def evaluate_proposal(self, proposal: Proposal) -> ProposalResponse:
        """
        Evaluates a proposal and returns a recommendation.

        :param proposal: The proposal to evaluate.
        :return: The agent's recommendation.
        """
        pass

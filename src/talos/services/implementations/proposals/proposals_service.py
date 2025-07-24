from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseLanguageModel
from pydantic import ConfigDict

from talos.models.proposals import Proposal, QueryResponse
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.abstract.proposal_agent import ProposalAgent
from talos.skills.proposals import ProposalsSkill


class ProposalsService(ProposalAgent):
    """
    A service for evaluating proposals using the ProposalsSkill.
    
    This service acts as a bridge between the abstract ProposalAgent interface
    and the concrete ProposalsSkill implementation.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    llm: BaseLanguageModel
    prompt_manager: PromptManager | None = None
    _skill: ProposalsSkill | None = None
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        
        if self.prompt_manager is None:
            self.prompt_manager = FilePromptManager("src/talos/prompts")
        
        self._skill = ProposalsSkill(
            llm=self.llm,
            prompt_manager=self.prompt_manager,
            rag_dataset=self.rag_dataset,
            tools=self.tools
        )
    
    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
        """
        Evaluates a proposal and returns a recommendation.
        
        :param proposal: The proposal to evaluate.
        :return: The agent's recommendation with confidence and reasoning.
        """
        if self._skill is None:
            raise RuntimeError("ProposalsSkill not initialized")
        
        return self._skill.evaluate_proposal(proposal)

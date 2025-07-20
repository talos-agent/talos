from __future__ import annotations

from typing import Any

from langchain.chains import LLMChain
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from pydantic import ConfigDict

from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.abstract import ProposalAgent
from talos.services.proposals.models import Proposal, QueryResponse


class ProposalsService(ProposalAgent):
    """
    A LangChain-based agent for evaluating proposals.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm: BaseLanguageModel
    prompt_manager: PromptManager
    rag_dataset: Any | None = None
    tools: list[Any] | None = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self.prompt_manager = FilePromptManager("src/talos/prompts")

    def run(self, **kwargs: Any) -> QueryResponse:
        if "proposal" in kwargs and "feedback" in kwargs:
            return self.evaluate_proposal(kwargs["proposal"], kwargs["feedback"])
        raise ValueError("Missing required arguments: proposal, feedback")

    def evaluate_proposal(self, proposal: Proposal, feedback: list[dict[str, Any]] | None = None) -> QueryResponse:
        """
        Evaluates a proposal and returns a recommendation.
        """
        prompt = self.prompt_manager.get_prompt("proposal_evaluation_prompt")
        if not prompt:
            raise ValueError("Prompt 'proposal_evaluation_prompt' not found.")
        prompt_template = PromptTemplate(
            template=prompt.template,
            input_variables=prompt.input_variables,
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        feedback_str = "\n".join([f"- {f.delegate}: {f.feedback}" for f in proposal.feedback])
        response = chain.run(
            proposal_text=proposal.proposal_text,
            feedback=feedback_str,
        )
        return QueryResponse(answers=[response])

from __future__ import annotations

import json
from typing import Any

from langchain.chains import LLMChain
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from pydantic import ConfigDict

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.single_prompt_manager import SinglePromptManager
from talos.services.abstract import ProposalAgent
from talos.services.proposals.models import Proposal, QueryResponse


def get_default_proposal_prompt() -> Prompt:
    with open("src/talos/prompts/proposal_evaluation_prompt.json") as f:
        prompt_data = json.load(f)
    return Prompt(
        name=prompt_data["name"],
        template=prompt_data["template"],
        input_variables=prompt_data["input_variables"],
    )


class ProposalsService(ProposalAgent):
    """
    A LangChain-based agent for evaluating proposals.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm: BaseLanguageModel
    prompt_manager: PromptManager = SinglePromptManager(get_default_proposal_prompt())
    rag_dataset: Any | None = None
    tools: list[Any] | None = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

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
        response = chain.invoke({"proposal_text": proposal.proposal_text, "feedback": feedback_str})
        return QueryResponse(answers=[response["text"]])

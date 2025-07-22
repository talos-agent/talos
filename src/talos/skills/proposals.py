from __future__ import annotations

import json
from typing import Any

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from pydantic import ConfigDict

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.single_prompt_manager import SinglePromptManager
from talos.models.proposals.models import Proposal, QueryResponse
from talos.skills.base import Skill


def get_default_proposal_prompt() -> Prompt:
    with open("src/talos/prompts/proposal_evaluation_prompt.json") as f:
        prompt_data = json.load(f)
    return Prompt(
        name=prompt_data["name"],
        template=prompt_data["template"],
        input_variables=prompt_data["input_variables"],
    )


class ProposalsSkill(Skill):
    """
    A skill for evaluating proposals.

    This skill takes a `Proposal` object as input, which contains the text of the
    proposal and any feedback from previous evaluations. It uses a large language
    model (LLM) to evaluate the proposal and returns a `QueryResponse` object
    containing the recommendation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm: BaseLanguageModel
    prompt_manager: PromptManager = SinglePromptManager(get_default_proposal_prompt())
    rag_dataset: Any | None = None
    tools: list[Any] | None = None

    @property
    def name(self) -> str:
        return "proposals_skill"

    def run(self, **kwargs: Any) -> QueryResponse:
        if "proposal" in kwargs:
            return self.evaluate_proposal(kwargs["proposal"])
        raise ValueError("Missing required arguments: proposal")

    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
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
        chain = prompt_template | self.llm
        feedback_str = "\n".join([f"- {f.delegate}: {f.feedback}" for f in proposal.feedback])
        response = chain.invoke({"proposal_text": proposal.proposal_text, "feedback": feedback_str})
        return QueryResponse(answers=[response.content])

from __future__ import annotations

import json
import logging
import re
from typing import Any

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from pydantic import ConfigDict

from talos.models.proposals import Feedback, Proposal, ProposalResponse
from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.single_prompt_manager import SinglePromptManager
from talos.skills.base import Skill


def get_default_proposal_prompt() -> Prompt:
    with open("src/talos/prompts/proposal_evaluation_prompt.json") as f:
        prompt_data = json.load(f)
    return Prompt(
        name=prompt_data["name"],
        template=prompt_data["template"],
        input_variables=prompt_data["input_variables"],
    )


def parse_proposal_file(filepath: str) -> Proposal:
    with open(filepath, "r") as f:
        content = f.read()

    proposal_match = re.search(r"\[PROPOSAL\]\n(.*?)\n\[FEEDBACK\]", content, re.DOTALL)
    feedback_match = re.search(r"\[FEEDBACK\]\n(.*)", content, re.DOTALL)

    proposal_text = proposal_match.group(1).strip() if proposal_match else ""
    feedback_text = feedback_match.group(1).strip() if feedback_match else ""

    feedback_list = []
    if feedback_text:
        for line in feedback_text.split("\n"):
            if ":" in line:
                delegate, feedback = line.split(":", 1)
                feedback_list.append(Feedback(delegate=delegate.strip(), feedback=feedback.strip()))

    return Proposal(proposal_text=proposal_text, feedback=feedback_list)


class ProposalsSkill(Skill):
    """
    A skill for evaluating proposals.

    This skill takes a `Proposal` object as input, which contains the text of the
    proposal and any feedback from previous evaluations. It uses a large language
    model (LLM) to evaluate the proposal and returns a `ProposalResponse` object
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

    def run(self, **kwargs: Any) -> ProposalResponse:
        if "filepath" not in kwargs:
            raise ValueError("Missing required argument: filepath")

        filepath = kwargs["filepath"]
        proposal = parse_proposal_file(filepath)
        return self.evaluate_proposal(proposal)

    def evaluate_proposal(self, proposal: Proposal) -> ProposalResponse:
        """
        Evaluates a proposal and returns a recommendation with confidence and reasoning.
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Evaluating proposal with {len(proposal.feedback)} feedback items")

        if not proposal.proposal_text or not proposal.proposal_text.strip():
            raise ValueError("Proposal text cannot be empty")

        prompt = self.prompt_manager.get_prompt("proposal_evaluation_prompt")
        if not prompt:
            raise ValueError("Prompt 'proposal_evaluation_prompt' not found.")

        try:
            prompt_template = PromptTemplate(
                template=prompt.template,
                input_variables=prompt.input_variables,
            )
            chain = prompt_template | self.llm

            feedback_str = (
                "\n".join([f"- {f.delegate}: {f.feedback}" for f in proposal.feedback])
                if proposal.feedback
                else "No delegate feedback provided."
            )

            logger.debug(f"Invoking LLM with proposal text length: {len(proposal.proposal_text)}")
            response = chain.invoke({"proposal_text": proposal.proposal_text, "feedback": feedback_str})

            content = response.content
            confidence_score = self._extract_confidence(content)
            reasoning = self._extract_reasoning(content)

            logger.info(f"Proposal evaluation completed with confidence: {confidence_score}")

            return ProposalResponse(answers=[content], confidence_score=confidence_score, reasoning=reasoning)

        except Exception as e:
            logger.error(f"Failed to evaluate proposal: {str(e)}")
            raise RuntimeError(f"Failed to evaluate proposal: {str(e)}") from e

    def _extract_confidence(self, content: str) -> float | None:
        """Extract confidence score from LLM response."""
        match = re.search(r"CONFIDENCE:\s*([0-9]*\.?[0-9]+)", content)
        if match:
            try:
                confidence = float(match.group(1))
                return max(0.0, min(1.0, confidence))
            except ValueError:
                pass
        return None

    def _extract_reasoning(self, content: str) -> str | None:
        """Extract reasoning from LLM response."""
        match = re.search(r"REASONING:\s*(.*)", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

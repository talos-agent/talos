from typing import Any

from langchain.chains import LLMChain
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate

from talos.services.abstract import ProposalAgent
from talos.services.proposals.models import Proposal, QueryResponse


class ProposalsService(ProposalAgent):
    """
    A LangChain-based agent for evaluating proposals.
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        rag_dataset: Any = None,
        tools: list[Any] | None = None,
    ):
        super().__init__(rag_dataset, tools if tools is not None else [])
        self.llm = llm

    def run(self, **kwargs: Any) -> QueryResponse:
        if "proposal" in kwargs and "feedback" in kwargs:
            return self.evaluate_proposal(kwargs["proposal"], kwargs["feedback"])
        raise ValueError("Missing required arguments: proposal, feedback")

    def evaluate_proposal(self, proposal: Proposal, feedback: list[dict[str, Any]]) -> QueryResponse:
        """
        Evaluates a proposal and returns a recommendation.
        """
        prompt_template = PromptTemplate(
            template=proposal.prompt,
            input_variables=["proposal_text", "feedback"],
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        response = chain.run(
            proposal_text=proposal.proposal_text,
            feedback="\n".join([f"- {f['delegate']}: {f['feedback']}" for f in feedback]),
        )
        return QueryResponse(answers=[response])

from typing import Any

from langchain.chains import LLMChain
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate

from talos.services.base import Service
from talos.services.proposals.models import Proposal, QueryResponse


class ProposalsService(Service):
    """
    A LangChain-based agent for evaluating proposals.
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        rag_dataset: Any = None,
        tools: list[Any] | None = None,
    ):
        self.llm = llm
        self.rag_dataset = rag_dataset
        self.tools = tools if tools is not None else []

    @property
    def name(self) -> str:
        return "proposals"

    def evaluate_proposal(
        self, proposal: "Proposal", feedback: list[dict[str, Any]]
    ) -> QueryResponse:
        """
        Evaluates a proposal and returns a recommendation.
        """
        from talos.services.proposals.models import Proposal
        prompt_template = PromptTemplate(
            template=proposal.prompt,
            input_variables=["proposal_text", "feedback"],
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        response = chain.run(
            proposal_text=proposal.proposal_text,
            feedback="\n".join(
                [f"- {f['delegate']}: {f['feedback']}" for f in feedback]
            ),
        )
        return QueryResponse(answers=[{"answer": response, "score": 1.0}])

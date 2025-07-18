from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate

from talos.disciplines.abstract import ProposalAgent
from talos.disciplines.proposals.models import Proposal, QueryResponse


class ProposalsDiscipline(ProposalAgent):
    """
    A LangChain-based agent for evaluating proposals.
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        rag_dataset: Any = None,
        tools: Optional[List[Any]] = None,
    ):
        super().__init__(rag_dataset, tools if tools is not None else [])
        self.llm = llm

    def evaluate_proposal(
        self, proposal: Proposal, feedback: List[Dict[str, Any]]
    ) -> QueryResponse:
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
            feedback="\n".join(
                [f"- {f['delegate']}: {f['feedback']}" for f in feedback]
            ),
        )
        return QueryResponse(answers=[{"answer": response, "score": 1.0}])

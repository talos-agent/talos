from typing import Any

from langchain.chains import LLMChain
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate

from talos.services.abstract import ProposalAgent
from talos.services.models import (
    QueryResponse,
    Ticket,
    TicketCreationRequest,
    TicketResult,
)
from talos.services.proposals.models import Proposal


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

    def create_ticket(self, request: "TicketCreationRequest") -> "Ticket":
        raise NotImplementedError

    def get_ticket_status(self, ticket_id: str) -> "Ticket":
        raise NotImplementedError

    def cancel_ticket(self, ticket_id: str) -> "Ticket":
        raise NotImplementedError

    def get_ticket_result(self, ticket_id: str) -> "TicketResult":
        raise NotImplementedError

    def evaluate_proposal(
        self, proposal: Proposal, feedback: list[dict[str, Any]]
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
        return QueryResponse(answers=[response])

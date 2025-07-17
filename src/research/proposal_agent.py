from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

from research.models import Proposal, QueryResponse
from research.proposal_agent_abc import ProposalAgent


class LangChainProposalAgent(ProposalAgent):
    """
    A LangChain-based agent for evaluating proposals.
    """

    def __init__(self, openai_api_key: str, model_name: str = "text-davinci-003"):
        self.llm = OpenAI(model_name=model_name, api_key=openai_api_key)

    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
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
                [f"- {f.delegate}: {f.feedback}" for f in proposal.feedback]
            ),
        )
        return QueryResponse(answers=[{"answer": response, "score": 1.0}])

import os

from langchain_openai import ChatOpenAI

from talos.models.proposals import Feedback, Proposal
from talos.services.implementations import ProposalsService


def run_proposal_example():
    """
    Runs an example of the agent evaluating a proposal.
    """
    # Initialize the proposals service
    service = ProposalsService(llm=ChatOpenAI(model="gpt-4o", openai_api_key=os.environ.get("OPENAI_API_KEY", "")))

    # Define the proposal
    proposal = Proposal(
        proposal_text="""
        **Proposal: Invest in a new DeFi protocol**

        **Description:**
        This proposal suggests that the treasury invest 10% of its assets in a
        new DeFi protocol called "SuperYield". The protocol promises high
        returns through a novel liquidity mining strategy.

        **Justification:**
        Investing in SuperYield could significantly increase the treasury's
        returns and diversify its portfolio.

        **Risks:**
        As a new protocol, SuperYield has a limited track record and may be
        vulnerable to smart contract exploits.
        """,
        feedback=[
            Feedback(
                delegate="Alice",
                feedback="I'm concerned about the security risks. Have there been any independent security audits?",
            ),
            Feedback(
                delegate="Bob",
                feedback="The potential returns are very attractive. I think it's worth the risk.",
            ),
        ],
    )

    # Evaluate the proposal
    response = service.evaluate_proposal(proposal)

    # Print the agent's recommendation
    print("--- Agent's Recommendation ---")
    print(response.answers[0])


if __name__ == "__main__":
    run_proposal_example()

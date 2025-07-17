import os

from conversational.main_agent import MainAgent
from research.models import Feedback, Proposal


def run_proposal_example():
    """
    Runs an example of the agent evaluating a proposal.
    """
    # Initialize the main agent
    agent = MainAgent(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        pinata_api_key=os.environ.get("PINATA_API_KEY", ""),
        pinata_secret_api_key=os.environ.get("PINATA_SECRET_API_KEY", ""),
    )

    # Define the proposal
    proposal = Proposal(
        prompt="""
        Please evaluate the following proposal and provide a recommendation.
        Consider the proposal's potential benefits, risks, and the feedback
        provided by the delegates.
        """,
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
    response = agent.evaluate_proposal(proposal)

    # Print the agent's recommendation
    print("--- Agent's Recommendation ---")
    print(response.answers[0].answer)


if __name__ == "__main__":
    run_proposal_example()

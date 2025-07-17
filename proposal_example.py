import os

from conversational.main_agent import MainAgent
from research.models import AddDatasetParams, RunParams


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

    # Add a relevant dataset
    agent.add_dataset(
        "https://en.wikipedia.org/wiki/Decentralized_autonomous_organization",
        params=AddDatasetParams(),
    )

    # Define the proposal
    proposal_prompt = """
    **Proposal: Invest in a new DeFi protocol**

    **Description:**
    This proposal suggests that the treasury invest 10% of its assets in a new
    DeFi protocol called "SuperYield". The protocol promises high returns
    through a novel liquidity mining strategy.

    **Justification:**
    Investing in SuperYield could significantly increase the treasury's returns
    and diversify its portfolio.

    **Risks:**
    As a new protocol, SuperYield has a limited track record and may be
    vulnerable to smart contract exploits.
    """

    # Simulate human feedback
    human_feedback = """
    I'm concerned about the security risks of investing in such a new
    protocol. Have there been any independent security audits?
    """

    # Combine the prompt and feedback for the agent
    full_prompt = f"""
    {proposal_prompt}

    **Human Feedback:**
    {human_feedback}

    **Agent's Task:**
    Please evaluate this proposal, considering the human feedback.
    Provide your analysis and a recommendation on whether to pass the
    proposal.
    """

    # Run the agent
    response = agent.run(full_prompt, params=RunParams(web_search=True))

    # Print the agent's recommendation
    print("--- Agent's Recommendation ---")
    print(response.answers[0].answer)


if __name__ == "__main__":
    run_proposal_example()

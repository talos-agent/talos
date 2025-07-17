from typing import Dict
from src.disciplines.base import Discipline
from src.disciplines.proposals.implementation.proposals import ProposalsDiscipline
from src.disciplines.twitter.implementation.twitter import TwitterDiscipline
from src.disciplines.github.implementation.github import GitHubDiscipline
from src.disciplines.onchain_management.implementation.onchain_management import OnChainManagementDiscipline
from src.disciplines.proposals.models import Proposal, QueryResponse, RunParams
from src.utils.ipfs import IPFSUtils


class MainAgent:
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    """

    def __init__(
        self,
        openai_api_key: str,
        pinata_api_key: str,
        pinata_secret_api_key: str,
    ):
        self.disciplines: Dict[str, Discipline] = {
            "proposals": ProposalsDiscipline(openai_api_key=openai_api_key),
            "twitter": TwitterDiscipline(),
            "github": GitHubDiscipline(),
            "onchain": OnChainManagementDiscipline(),
        }
        self.ipfs_utils = IPFSUtils(
            pinata_api_key=pinata_api_key,
            pinata_secret_api_key=pinata_secret_api_key,
        )

    def run(self, query: str, params: RunParams) -> QueryResponse:
        """
        Runs the appropriate agent based on the query and parameters.
        """
        if "ipfs publish" in query.lower():
            file_path = query.split(" ")[-1]
            ipfs_hash = self.ipfs_utils.publish(file_path)
            return QueryResponse(
                answers=[{"answer": f"Published to IPFS with hash: {ipfs_hash}", "score": 1.0}]
            )
        elif "ipfs read" in query.lower():
            ipfs_hash = query.split(" ")[-1]
            content = self.ipfs_utils.read(ipfs_hash)
            return QueryResponse(answers=[{"answer": content.decode(), "score": 1.0}])

        # This is a temporary way to route to the correct discipline.
        # A more sophisticated routing mechanism will be needed in the future.
        if params.discipline in self.disciplines:
            discipline = self.disciplines[params.discipline]
            # This is a placeholder for actually calling the discipline
            return QueryResponse(answers=[{"answer": f"Using {discipline.name} discipline", "score": 1.0}])
        else:
            return QueryResponse(answers=[{"answer": "No discipline specified", "score": 1.0}])

    def evaluate_proposal(self, proposal: Proposal) -> QueryResponse:
        """
        Evaluates a proposal.
        """
        proposals_discipline = self.disciplines.get("proposals")
        if proposals_discipline:
            return proposals_discipline.evaluate_proposal(proposal)
        else:
            return QueryResponse(answers=[{"answer": "Proposals discipline not loaded", "score": 0.0}])

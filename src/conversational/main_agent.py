
from conversational.agent import LangChainConversationalAgent
from research.agent import LangChainAgent
from research.models import AddDatasetParams, QueryResponse, RunParams


from utils.ipfs import IPFSUtils


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
        self.conversational_agent = LangChainConversationalAgent(
            openai_api_key=openai_api_key
        )
        self.research_agent = LangChainAgent(openai_api_key=openai_api_key)
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
            return QueryResponse(answers=[{"answer": f"Published to IPFS with hash: {ipfs_hash}", "score": 1.0}])
        elif "ipfs read" in query.lower():
            ipfs_hash = query.split(" ")[-1]
            content = self.ipfs_utils.read(ipfs_hash)
            return QueryResponse(answers=[{"answer": content.decode(), "score": 1.0}])
        elif params.web_search or "research" in query.lower():
            return self.research_agent.run(query, params)
        else:
            return self.conversational_agent.run(query, params)

    def add_dataset(self, dataset_path: str, params: AddDatasetParams) -> None:
        """
        Adds a dataset to the research agent.
        """
        self.research_agent.add_dataset(dataset_path, params)

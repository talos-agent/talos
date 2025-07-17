
from conversational.langchain_agent import LangChainConversationalAgent
from research.langchain_agent import LangChainAgent
from research.models import AddDatasetParams, QueryResponse, RunParams


class MainAgent:
    """
    A top-level agent that delegates to a conversational agent and a research agent.
    """

    def __init__(self, openai_api_key: str):
        self.conversational_agent = LangChainConversationalAgent(
            openai_api_key=openai_api_key
        )
        self.research_agent = LangChainAgent(openai_api_key=openai_api_key)

    def run(self, query: str, params: RunParams) -> QueryResponse:
        """
        Runs the appropriate agent based on the query and parameters.
        """
        if params.web_search or "research" in query.lower():
            return self.research_agent.run(query, params)
        else:
            return self.conversational_agent.run(query, params)

    def add_dataset(self, dataset_path: str, params: AddDatasetParams) -> None:
        """
        Adds a dataset to the research agent.
        """
        self.research_agent.add_dataset(dataset_path, params)

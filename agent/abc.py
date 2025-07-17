from abc import ABC, abstractmethod

from agent.models import AddDatasetParams, QueryResponse, RunParams


class Agent(ABC):
    """
    An abstract base class for an agent that can process queries and return results.
    """

    @abstractmethod
    def run(self, query: str, params: RunParams) -> QueryResponse:
        """
        Runs the agent with a given query and optional parameters.

        :param query: The query to process.
        :param params: Parameters for the agent.
        :return: The results of the query.
        """
        pass

    @abstractmethod
    def add_dataset(self, dataset_path: str, params: AddDatasetParams) -> None:
        """
        Adds a dataset to the agent's knowledge base.

        :param dataset_path: The path to the dataset.
        :param params: Parameters for adding the dataset.
        """
        pass

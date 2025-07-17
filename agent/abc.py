from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class Agent(ABC):
    """
    An abstract base class for an agent that can process queries and return results.
    """

    @abstractmethod
    def run(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Runs the agent with a given query and optional parameters.

        :param query: The query to process.
        :param params: Optional parameters for the agent.
        :return: A list of dictionaries representing the results.
        """
        pass

    @abstractmethod
    def add_dataset(self, dataset_path: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Adds a dataset to the agent's knowledge base.

        :param dataset_path: The path to the dataset.
        :param params: Optional parameters for adding the dataset.
        """
        pass

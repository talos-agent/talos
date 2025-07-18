from abc import ABC, abstractmethod


class Tool(ABC):
    """
    An abstract base class for a tool.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the tool.
        """
        pass

    @abstractmethod
    def run(self, **kwargs) -> str:
        """
        Runs the tool.
        """
        pass

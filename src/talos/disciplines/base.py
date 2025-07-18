from abc import ABC, abstractmethod


class Discipline(ABC):
    """
    An abstract base class for a discipline.

    Disciplines are LLM-driven actions that can be performed by the agent.
    They are the primary way that the agent interacts with the world.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the discipline.
        """
        pass

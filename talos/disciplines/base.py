from abc import ABC, abstractmethod


class Discipline(ABC):
    """
    An abstract base class for a discipline.

    Disciplines are a way to organize and manage the agent's actions.
    They are LLM driven actions, which means that they are powered by a
    language model. This allows them to be more flexible and powerful
    than traditional tools.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the discipline.
        """
        pass

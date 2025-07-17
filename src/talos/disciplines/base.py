from abc import ABC, abstractmethod


class Discipline(ABC):
    """
    An abstract base class for a discipline.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the discipline.
        """
        pass

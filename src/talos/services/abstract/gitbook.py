from abc import ABC, abstractmethod

from talos.services.base import Service


class GitBook(Service, ABC):
    """
    An abstract base class for a GitBook service.
    """

    @abstractmethod
    def update(self, query: str) -> None:
        """
        Takes a command/query and uses the instruction to help it update the gitbook.
        """
        pass

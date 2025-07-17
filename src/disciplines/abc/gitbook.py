from abc import ABC, abstractmethod


class GitBook(ABC):
    """
    An abstract base class for a GitBook discipline.
    """

    @abstractmethod
    def read_page(self, page_url: str) -> str:
        """
        Reads a GitBook page.
        """
        pass

    @abstractmethod
    def update_page(self, page_url: str, content: str) -> None:
        """
        Updates a GitBook page.
        """
        pass

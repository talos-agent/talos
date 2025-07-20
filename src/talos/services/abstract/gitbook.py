from abc import ABC, abstractmethod


class GitBook(ABC):
    @abstractmethod
    def create_page(self, title: str, content: str) -> None:
        pass

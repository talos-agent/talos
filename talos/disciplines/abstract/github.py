from abc import ABC, abstractmethod
from langchain_core.language_models import BaseLanguageModel


class GitHub(ABC):
    """
    An abstract base class for a GitHub discipline.
    """

    def __init__(self, llm: BaseLanguageModel, token: str):
        self.llm = llm
        self.token = token

    @abstractmethod
    def reply_to_issues(self, user: str, project: str) -> None:
        """
        Replies to issues that are pending Talos feedback.
        """
        pass

    @abstractmethod
    def review_pull_requests(self, user: str, project: str) -> None:
        """
        Reviews pending pull requests to determine if they're ready for approval or not.
        """
        pass

    @abstractmethod
    def scan(self, user: str, project: str) -> str:
        """
        Reviews the code in a repository.
        """
        pass

    @abstractmethod
    def reference_code(self, user: str, project: str, query: str) -> str:
        """
        Looks at the directory structure and any files in the repository to answer a query.
        """
        pass

    @abstractmethod
    def update_summary(self, user: str, project: str) -> None:
        """
        Updates the SUMMARY.md for a repo to make it easier to review it.
        """
        pass

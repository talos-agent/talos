from abc import ABC, abstractmethod


class GitHub(ABC):
    """
    An abstract base class for a GitHub discipline.
    """

    @abstractmethod
    def read_issue(self, issue_url: str) -> str:
        """
        Reads a GitHub issue.
        """
        pass

    @abstractmethod
    def reply_to_issue(self, issue_url: str, comment: str) -> None:
        """
        Replies to a GitHub issue.
        """
        pass

    @abstractmethod
    def review_pr(self, pr_url: str, feedback: str) -> None:
        """
        Reviews a pull request.
        """
        pass

    @abstractmethod
    def merge_pr(self, pr_url: str) -> None:
        """
        Merges a pull request.
        """
        pass

    @abstractmethod
    def scan_for_malicious_code(self, pr_url: str) -> bool:
        """
        Scans a pull request for malicious code.
        """
        pass

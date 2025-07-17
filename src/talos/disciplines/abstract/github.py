from abc import ABC, abstractmethod
from typing import List
from .models import Issue, Comment, PullRequestFile


class GitHub(ABC):
    """
    An abstract base class for a GitHub discipline.
    """

    @abstractmethod
    def read_issue(self, user: str, project: str, issue_number: int) -> str:
        """
        Reads a GitHub issue.
        """
        pass

    @abstractmethod
    def reply_to_issue(self, user: str, project: str, issue_number: int, comment: str) -> None:
        """
        Replies to a GitHub issue.
        """
        pass

    @abstractmethod
    def review_pr(self, user: str, project: str, pr_number: int, feedback: str) -> None:
        """
        Reviews a pull request.
        """
        pass

    @abstractmethod
    def merge_pr(self, user: str, project: str, pr_number: int) -> None:
        """
        Merges a pull request.
        """
        pass

    @abstractmethod
    def get_open_issues(self, user: str, project: str) -> List[Issue]:
        """
        Gets all open issues in a repository.
        """
        pass

    @abstractmethod
    def get_issue_comments(self, user: str, project: str, issue_number: int) -> List[Comment]:
        """
        Gets all comments for an issue.
        """
        pass

    @abstractmethod
    def get_pr_files(self, user: str, project: str, pr_number: int) -> List[PullRequestFile]:
        """
        Gets all files in a pull request.
        """
        pass

    @abstractmethod
    def get_project_structure(self, user: str, project: str, path: str = "") -> List[str]:
        """
        Gets the project structure.
        """
        pass

    @abstractmethod
    def get_file_content(self, user: str, project: str, filepath: str) -> str:
        """
        Gets the content of a file.
        """
        pass

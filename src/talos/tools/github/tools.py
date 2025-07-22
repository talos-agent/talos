import os
from typing import Any

import requests
from github import Auth, Github
from pydantic import BaseModel, Field, PrivateAttr


class GithubTools(BaseModel):
    """
    A collection of tools for interacting with the Github API.
    """

    token: str | None = Field(default_factory=lambda: os.environ.get("GITHUB_API_TOKEN"))
    _github: Github = PrivateAttr()
    _headers: dict[str, str] = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        if not self.token:
            raise ValueError("Github token not provided.")
        self._github = Github(auth=Auth.Token(self.token))
        self._headers = {"Authorization": f"token {self.token}"}

    def get_open_issues(self, user: str, project: str) -> list[dict[str, Any]]:
        """
        Gets all open issues for a given repository.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        return [
            {"number": issue.number, "title": issue.title, "url": issue.html_url}
            for issue in repo.get_issues(state="open")
        ]

    def get_all_pull_requests(self, user: str, project: str, state: str = "open") -> list[dict[str, Any]]:
        """
        Gets all pull requests for a given repository.

        :param state: Can be one of 'open', 'closed', or 'all'.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        return [{"number": pr.number, "title": pr.title, "url": pr.html_url} for pr in repo.get_pulls(state=state)]

    def get_issue_comments(self, user: str, project: str, issue_number: int) -> list[dict[str, Any]]:
        """
        Gets all comments for a given issue.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        issue = repo.get_issue(number=issue_number)
        comments = []
        for comment in issue.get_comments():
            comments.append(
                {
                    "user": comment.user.login,
                    "comment": comment.body,
                    "reply_to": None,  # PyGithub does not support this directly
                }
            )
        return comments

    def get_pr_comments(self, user: str, project: str, pr_number: int) -> list[dict[str, Any]]:
        """
        Gets all comments for a given pull request.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(pr_number)
        comments = []
        for comment in pr.get_issue_comments():
            comments.append(
                {
                    "user": comment.user.login,
                    "comment": comment.body,
                }
            )
        return comments

    def reply_to_issue(self, user: str, project: str, issue_number: int, comment: str) -> None:
        """
        Replies to a given issue.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        issue = repo.get_issue(number=issue_number)
        issue.create_comment(comment)

    def get_pr_files(self, user: str, project: str, pr_number: int) -> list[str]:
        """
        Gets all files for a given pull request.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        return [file.filename for file in pr.get_files()]

    def get_pr_diff(self, user: str, project: str, pr_number: int) -> str:
        """
        Gets the diff for a given pull request.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        response = requests.get(pr.patch_url, headers=self._headers)
        response.raise_for_status()
        return response.text

    def get_project_structure(self, user: str, project: str, path: str = "") -> list[str]:
        """
        Gets the project structure for a given repository.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        contents = repo.get_contents(path)
        if isinstance(contents, list):
            return [content.path for content in contents]
        return [contents.path]

    def get_file_content(self, user: str, project: str, filepath: str) -> str:
        """
        Gets the content of a file.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        content = repo.get_contents(filepath)
        if isinstance(content, list):
            raise ValueError("Path is a directory, not a file.")
        return content.decoded_content.decode()

    def merge_pr(self, user: str, project: str, pr_number: int) -> None:
        """
        Merges a pull request.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.merge()

    def review_pr(self, user: str, project: str, pr_number: int, feedback: str) -> None:
        """
        Reviews a pull request.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.create_review(body=feedback, event="COMMENT")

    def comment_on_pr(self, user: str, project: str, pr_number: int, comment: str) -> None:
        """
        Comments on a pull request.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.create_issue_comment(comment)

    def approve_pr(self, user: str, project: str, pr_number: int) -> None:
        """
        Approves a pull request.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.create_review(event="APPROVE")

    def create_issue(self, user: str, project: str, title: str, body: str) -> dict[str, Any]:
        """
        Creates a new issue.
        """
        repo = self._github.get_repo(f"{user}/{project}")
        issue = repo.create_issue(title=title, body=body)
        return {"number": issue.number, "title": issue.title, "url": issue.html_url}

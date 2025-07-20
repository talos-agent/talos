from __future__ import annotations

from typing import Any

from pydantic import PrivateAttr

from talos.services.base import Service
from talos.services.github_agent import GithubPRReviewAgent
from talos.tools.github.tools import GithubTools


class GithubService(Service):
    """
    A service for reviewing Github pull requests.
    """

    _tools: GithubTools = PrivateAttr()
    _agent: GithubPRReviewAgent = PrivateAttr()

    def __init__(self, token: str, **kwargs: Any):
        super().__init__(**kwargs)
        self._tools = GithubTools(token=token)
        self._agent = GithubPRReviewAgent(token)

    @property
    def name(self) -> str:
        return "github_pr_review"

    def run(self, **kwargs: Any) -> str:
        user = kwargs.get("user")
        repo = kwargs.get("repo")
        pr_number = kwargs.get("pr_number")
        if not user or not repo or not pr_number:
            raise ValueError("user, repo, and pr_number are required")

        diff = self._tools.get_pr_diff(user, repo, pr_number)
        comments = self._tools.get_pr_comments(user, repo, pr_number)
        files = self._tools.get_pr_files(user, repo, pr_number)

        input_str = f"Diff: {diff}\n\nComments: {comments}\n\nFiles: {files}"
        response = self._agent.run(input=input_str, user=user, project=repo)
        return response["output"]

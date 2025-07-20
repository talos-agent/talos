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

    token: str

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._tools = GithubTools(token=self.token)
        self._agent = GithubPRReviewAgent(token=self.token)

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

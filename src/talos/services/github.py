from __future__ import annotations

from typing import Any

from pydantic import BaseModel, PrivateAttr

from talos.services.github_agent import GithubPRReviewAgent
from talos.tools.github.tools import GithubTools


class GithubService(BaseModel):
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

    def review_pr(self, user: str, repo: str, pr_number: int) -> str:

        diff = self._tools.get_pr_diff(user, repo, pr_number)
        comments = self._tools.get_pr_comments(user, repo, pr_number)
        files = self._tools.get_pr_files(user, repo, pr_number)

        input_str = f"Diff: {diff}\n\nComments: {comments}\n\nFiles: {files}"
        response = self._agent.run(input=input_str, user=user, project=repo)
        return response["output"]

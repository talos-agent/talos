from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from talos.services.github import GithubService


class TestGithubService(unittest.TestCase):
    @patch("talos.services.github.GithubTools")
    @patch("talos.services.github.GithubPRReviewAgent")
    def test_run(
        self,
        mock_github_pr_review_agent: MagicMock,
        mock_github_tools: MagicMock,
    ) -> None:
        # Arrange
        mock_github_tools_instance = mock_github_tools.return_value
        mock_github_tools_instance.get_pr_diff.return_value = "diff"
        mock_github_tools_instance.get_pr_comments.return_value = "comments"
        mock_github_tools_instance.get_pr_files.return_value = ["file1.py", "file2.py"]

        mock_agent_instance = mock_github_pr_review_agent.return_value
        mock_agent_instance.run.return_value = {"output": "feedback"}

        service = GithubService(token="test_token")

        # Act
        result = service.run(user="test_user", repo="test_repo", pr_number=1)

        # Assert
        self.assertEqual(result, "feedback")
        mock_github_tools_instance.get_pr_diff.assert_called_once_with("test_user", "test_repo", 1)
        mock_github_tools_instance.get_pr_comments.assert_called_once_with("test_user", "test_repo", 1)
        mock_github_tools_instance.get_pr_files.assert_called_once_with("test_user", "test_repo", 1)
        mock_agent_instance.run.assert_called_once_with(
            input="Diff: diff\n\nComments: comments\n\nFiles: ['file1.py', 'file2.py']",
            user="test_user",
            project="test_repo",
        )


if __name__ == "__main__":
    unittest.main()

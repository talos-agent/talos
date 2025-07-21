from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from talos.tools.github.tools import GithubTools


class TestGithubTools(unittest.TestCase):
    @patch("talos.tools.github.tools.Github")
    def test_create_issue(self, mock_github: MagicMock) -> None:
        # Arrange
        mock_github_instance = mock_github.return_value
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_issue.title = "Test Issue"
        mock_issue.html_url = "http://example.com/issue/123"
        mock_repo.create_issue.return_value = mock_issue
        mock_github_instance.get_repo.return_value = mock_repo

        tools = GithubTools(token="test_token")

        # Act
        result = tools.create_issue(
            user="test_user",
            project="test_repo",
            title="Test Issue",
            body="This is a test issue.",
        )

        # Assert
        self.assertEqual(
            result,
            {
                "number": 123,
                "title": "Test Issue",
                "url": "http://example.com/issue/123",
            },
        )
        mock_github_instance.get_repo.assert_called_once_with("test_user/test_repo")
        mock_repo.create_issue.assert_called_once_with(title="Test Issue", body="This is a test issue.")

    @patch("talos.tools.github.tools.Github")
    def test_get_all_pull_requests(self, mock_github: MagicMock) -> None:
        # Arrange
        mock_github_instance = mock_github.return_value
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.number = 1
        mock_pr.title = "Test PR"
        mock_pr.html_url = "http://example.com/pr/1"
        mock_repo.get_pulls.return_value = [mock_pr]
        mock_github_instance.get_repo.return_value = mock_repo

        tools = GithubTools(token="test_token")

        # Act
        result = tools.get_all_pull_requests(user="test_user", project="test_repo", state="all")

        # Assert
        self.assertEqual(
            result,
            [
                {
                    "number": 1,
                    "title": "Test PR",
                    "url": "http://example.com/pr/1",
                }
            ],
        )
        mock_github_instance.get_repo.assert_called_once_with("test_user/test_repo")
        mock_repo.get_pulls.assert_called_once_with(state="all")

    @patch("talos.tools.github.tools.Github")
    def test_comment_on_pr(self, mock_github: MagicMock) -> None:
        # Arrange
        mock_github_instance = mock_github.return_value
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_repo.get_pull.return_value = mock_pr
        mock_github_instance.get_repo.return_value = mock_repo

        tools = GithubTools(token="test_token")

        # Act
        tools.comment_on_pr(user="test_user", project="test_repo", pr_number=1, comment="Test comment")

        # Assert
        mock_github_instance.get_repo.assert_called_once_with("test_user/test_repo")
        mock_repo.get_pull.assert_called_once_with(number=1)
        mock_pr.create_issue_comment.assert_called_once_with("Test comment")

    @patch("talos.tools.github.tools.Github")
    def test_approve_pr(self, mock_github: MagicMock) -> None:
        # Arrange
        mock_github_instance = mock_github.return_value
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_repo.get_pull.return_value = mock_pr
        mock_github_instance.get_repo.return_value = mock_repo

        tools = GithubTools(token="test_token")

        # Act
        tools.approve_pr(user="test_user", project="test_repo", pr_number=1)

        # Assert
        mock_github_instance.get_repo.assert_called_once_with("test_user/test_repo")
        mock_repo.get_pull.assert_called_once_with(number=1)
        mock_pr.create_review.assert_called_once_with(event="APPROVE")


if __name__ == "__main__":
    unittest.main()

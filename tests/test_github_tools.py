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


if __name__ == "__main__":
    unittest.main()

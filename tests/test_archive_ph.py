from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from talos.tools.archive_ph import ArchivePhTool


class TestArchivePhTool(unittest.TestCase):
    @patch("requests.post")
    def test_run_success(self, mock_post: Mock) -> None:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.url = "https://archive.ph/2024.01.01/https://example.com/"
        mock_post.return_value = mock_response

        tool = ArchivePhTool()
        result = tool._run("https://example.com")

        self.assertEqual(result, "https://archive.ph/2024.01.01/https://example.com/")
        mock_post.assert_called_once_with("https://archive.ph/submit/", data={"url": "https://example.com"})

    @patch("requests.post")
    def test_run_error(self, mock_post: Mock) -> None:
        mock_post.side_effect = Exception("Test error")

        tool = ArchivePhTool()
        result = tool._run("https://example.com")

        self.assertEqual(result, "An error occurred: Test error")
        mock_post.assert_called_once_with("https://archive.ph/submit/", data={"url": "https://example.com"})


if __name__ == "__main__":
    unittest.main()

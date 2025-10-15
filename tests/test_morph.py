from __future__ import annotations

import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from talos.cli.main import app


class TestMorph(unittest.TestCase):
    @patch("talos.services.morph.MorphService.get_latest_block_number")
    def test_get_block_number(self, mock_get_latest_block_number):
        # Arrange
        mock_get_latest_block_number.return_value = 12345
        runner = CliRunner()

        # Act
        result = runner.invoke(app, ["morph", "get-block-number"])

        # Assert
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Latest block number: 12345", result.stdout)


if __name__ == "__main__":
    unittest.main()

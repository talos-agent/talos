from __future__ import annotations

import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from talos.cli.main import app


class TestUniaoLives(unittest.TestCase):
    @patch("os.system")
    def test_deploy(self, mock_system):
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(app, ["uniaolives", "deploy"])

        # Assert
        self.assertEqual(result.exit_code, 0)
        mock_system.assert_called_once_with("./deploy.sh")


if __name__ == "__main__":
    unittest.main()

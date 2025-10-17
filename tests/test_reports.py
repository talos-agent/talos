from __future__ import annotations

import unittest

from typer.testing import CliRunner

from talos.cli.main import app


class TestReports(unittest.TestCase):
    def test_gerar_relatorio(self):
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(app, ["gerar-relatorio"])

        # Assert
        self.assertEqual(result.exit_code, 0)
        self.assertIn("O Sismógrafo da Psique", result.stdout)
        self.assertIn("Missão Aletheia", result.stdout)


if __name__ == "__main__":
    unittest.main()

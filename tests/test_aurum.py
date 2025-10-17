from __future__ import annotations

import unittest

from typer.testing import CliRunner

from talos.aurum.grid import AurumGrid
from talos.cli.main import app


class TestAurumGrid(unittest.TestCase):
    def test_aurum_grid_instantiation(self):
        # Arrange
        grid = AurumGrid(phi=1.0, psi=1.0, omega=0.5)

        # Act
        coherence = grid.coherence

        # Assert
        self.assertEqual(coherence, 2.0)

    def test_aurum_cli_status(self):
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(app, ["aurum", "status"])

        # Assert
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Φ: 0.0", result.stdout)
        self.assertIn("Ψ: 0.0", result.stdout)
        self.assertIn("Ω: 0.0", result.stdout)


if __name__ == "__main__":
    unittest.main()

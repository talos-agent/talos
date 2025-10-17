from __future__ import annotations

import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from talos.cli.main import app


class TestAnchor(unittest.TestCase):
    @patch("talos.cli.main.csv_anchor_reward")
    def test_anchor_csv(self, mock_csv_anchor_reward):
        # Arrange
        mock_csv_anchor_reward.return_value = {
            "btcTx": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "amount": "1000000000000000000",
            "hash": "f2e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }
        runner = CliRunner()

        # Act
        with patch.dict(
            "os.environ",
            {
                "PRIVATE_KEY": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
                "TIMECHAIN_REWARD_ADDR": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
            },
        ):
            result = runner.invoke(
                app,
                [
                    "anchor",
                    "csv",
                    "1760574120,admin_releasetransactionquarantine,0x62964b2859f983fc1887b2015a35664e66d9bf25ae750e43571b504efcc3a680",
                ],
            )

        # Assert
        self.assertEqual(result.exit_code, 0)
        self.assertIn("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", result.stdout)

    @patch("talos.cli.main.decode_csv_line")
    def test_decode_csv(self, mock_decode_csv_line):
        # Arrange
        mock_decode_csv_line.return_value = "Decoded"
        runner = CliRunner()

        # Act
        result = runner.invoke(
            app,
            [
                "anchor",
                "csv",
                "1760574120,admin_releasetransactionquarantine,0x62964b2859f983fc1887b2015a35664e66d9bf25ae750e43571b504efcc3a680",
                "--decode",
            ],
        )

        # Assert
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Decoded", result.stdout)


if __name__ == "__main__":
    unittest.main()

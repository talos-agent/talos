import unittest
from unittest.mock import patch

from talos.tools.query_generator import QueryGeneratorTool


class TestQueryGeneratorTool(unittest.TestCase):
    @patch("talos.tools.query_generator.verify_checksum")
    @patch("talos.tools.query_generator.parse_log_string")
    def test_query_generator_tool(self, mock_parse_log_string, mock_verify_checksum):
        # Arrange
        mock_parse_log_string.return_value = {
            "timestamp_iso": "2025-10-16T15:26:00",
            "prefix": "E1823612",
        }
        mock_verify_checksum.return_value = True
        tool = QueryGeneratorTool(raw_log="E18236120202510161526s002d9797d9")

        # Act
        result = tool._run_unsupervised(raw_log="E18236120202510161526s002d9797d9")

        # Assert
        self.assertIn("Checksum valid. Queries generated:", result)
        self.assertIn("SELECT * FROM logs", result)
        self.assertIn("SELECT * FROM eventos", result)
        self.assertIn("echo 'E18236120202510161526s002d9797d9'", result)


if __name__ == "__main__":
    unittest.main()

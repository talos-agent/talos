import unittest

from talos.models.workflows import WorkflowVariables
from talos.utils.log_parser import parse_log_string, verify_checksum


class TestLogParser(unittest.TestCase):
    def test_parse_log_string_valid(self):
        # Arrange
        raw_log = "E18236120202510161526s002d9797d9"

        # Act
        result = parse_log_string(raw_log)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, WorkflowVariables)
        self.assertEqual(result.prefix, "E1823612")
        self.assertEqual(result.timestamp_iso, "2025-10-16T15:26:00")
        self.assertEqual(result.timestamp_raw, "0202510161526")
        self.assertEqual(result.separator, "s")
        self.assertEqual(result.suffix_hex, "002d9797d9")
        self.assertEqual(result.checksum_base, "E18236120202510161526s")

    def test_parse_log_string_invalid(self):
        # Arrange
        raw_log = "invalid_log_string"

        # Act
        result = parse_log_string(raw_log)

        # Assert
        self.assertIsNone(result)

    def test_verify_checksum_valid(self):
        # Arrange
        data = WorkflowVariables(
            prefix="E1823612",
            timestamp_iso="2025-10-16T15:26:00",
            timestamp_raw="0202510161526",
            separator="s",
            suffix_hex="d9797d9",
            checksum_base="E18236120202510161526s002",
        )

        # Act
        result = verify_checksum(data)

        # Assert
        self.assertTrue(result)

    def test_verify_checksum_invalid(self):
        # Arrange
        data = WorkflowVariables(
            prefix="E1823612",
            timestamp_iso="2025-10-16T15:26:00",
            timestamp_raw="0202510161526",
            separator="s",
            suffix_hex="invalid",
            checksum_base="E18236120202510161526s002",
        )

        # Act
        result = verify_checksum(data)

        # Assert
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

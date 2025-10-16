from __future__ import annotations

from typing import Any

from pydantic import Field

from talos.tools.base import SupervisedTool
from talos.utils.log_parser import parse_log_string, verify_checksum


class QueryGeneratorTool(SupervisedTool):
    """A tool to generate queries from a raw log string."""

    name: str = "query_generator"
    description: str = "Parses a raw log string, verifies its checksum, and generates SQL and shell queries."
    raw_log: str = Field(..., description="The raw log string to parse.")

    def _run_unsupervised(self, raw_log: str, **kwargs: Any) -> str:
        """Generates the queries after parsing and checksum verification."""
        parsed_data = parse_log_string(raw_log)
        if not parsed_data:
            return "Error: Invalid log string format."

        checksum_valid = verify_checksum(parsed_data)
        if not checksum_valid:
            return "Error: Checksum verification failed."

        ts_filter = parsed_data.timestamp_iso[:16]
        prefix_filter = parsed_data.prefix

        sql_query_1 = f"SELECT * FROM logs WHERE ts >= '{ts_filter}:00' AND ts < '{ts_filter}:59';"
        sql_query_2 = f"SELECT * FROM eventos WHERE codigo = '{prefix_filter}' AND ts = '{ts_filter}:00';"
        shell_query = f"echo '{raw_log}' | awk -F 's' '{{print \"Prefixo: \" substr($1, 1, 8) \" Data: \" substr($1, 9, 14) \" Checksum: \" substr($2, 3)}}'"

        return (
            f"Checksum valid. Queries generated:\n\n"
            f"SQL Query 1:\n{sql_query_1}\n\n"
            f"SQL Query 2:\n{sql_query_2}\n\n"
            f"Shell Query:\n{shell_query}"
        )

from __future__ import annotations

from datetime import datetime


def decode_csv_line(csv_line: str) -> str:
    """
    Decodes a CSV line into a human-readable format.

    Args:
        csv_line: The CSV line to decode.

    Returns:
        A human-readable string representing the CSV line.
    """
    ts, action, tx_hash = csv_line.split(",")
    date = datetime.fromtimestamp(int(ts), tz=datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
    return f"""
📅 Data (UTC):  {date}
🔍 Ação:        {action}
🔗 TxHash:      {tx_hash}
"""

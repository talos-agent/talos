from __future__ import annotations

from datetime import datetime

from talos.models.workflows import WorkflowVariables


def parse_log_string(raw: str) -> WorkflowVariables | None:
    """Parses a raw log string into a WorkflowVariables object."""
    try:
        prefix = raw[:8]
        timestamp_raw = raw[8:24]
        separator = raw[24]
        suffix = raw[25:]
        base_for_checksum = raw[:25]

        if len(timestamp_raw) == 16:
            ts_core = timestamp_raw[4:14]  # YYYYMMDDhhmm: 202510161526
            ts_format = "%Y%m%d%H%M"
        else:
            ts_core = timestamp_raw
            ts_format = "%Y%m%d%H%M%S"

        dt = datetime.strptime(ts_core, ts_format)

        return WorkflowVariables(
            prefix=prefix,
            timestamp_iso=dt.isoformat(),
            timestamp_raw=timestamp_raw,
            separator=separator,
            suffix_hex=suffix,
            checksum_base=base_for_checksum,
        )

    except (ValueError, IndexError) as e:
        print(f"Error parsing log string: {e}")
        return None


def verify_checksum(data: WorkflowVariables) -> bool:
    """Verifies the CRC-32 checksum of the parsed log data."""
    import binascii

    base = data.checksum_base.encode()
    suffix_target = data.suffix_hex.lstrip("0")

    crc = binascii.crc32(base) & 0xFFFFFFFF
    return f"{crc:x}".lstrip("0") == suffix_target.lstrip("0")

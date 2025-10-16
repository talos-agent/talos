from __future__ import annotations

from pydantic import BaseModel


class WorkflowVariables(BaseModel):
    """A model to hold the structured data from a parsed log string."""

    prefix: str
    timestamp_iso: str
    timestamp_raw: str
    separator: str
    suffix_hex: str
    checksum_base: str

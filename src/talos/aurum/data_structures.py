from __future__ import annotations

from pydantic import BaseModel, Field


class AurumHash(BaseModel):
    """
    Represents a 256-bit Aurum-Hash.
    """

    hash_value: str = Field(..., max_length=64, min_length=64)


class VertexFold(BaseModel):
    """
    Represents a vertex fold, which generates an Aurum-Hash.
    """

    vertex_a: str
    vertex_b: str
    aurum_hash: AurumHash

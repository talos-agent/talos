from __future__ import annotations

from typing import Any, List

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeVertex(BaseModel):
    id: str
    label: str
    point: Any  # Expected to be np.ndarray


class SimplexEdge(BaseModel):
    v1: str
    v2: str
    weight: float


class SimplexTriangle(BaseModel):
    v1: str
    v2: str
    v3: str


class SimplicialComplexSnapshot(BaseModel):
    """
    Knowledge representation as a simplicial complex for topological analysis.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vertices: List[KnowledgeVertex] = Field(default_factory=list)
    edges: List[SimplexEdge] = Field(default_factory=list)
    triangles: List[SimplexTriangle] = Field(default_factory=list)
    betti_numbers: List[int] = Field(default_factory=lambda: [1, 0, 0])

    def calculate_euler_characteristic(self) -> int:
        return len(self.vertices) - len(self.edges) + len(self.triangles)

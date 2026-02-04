from __future__ import annotations

import numpy as np
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from pydantic import BaseModel, ConfigDict, Field

class ContextDomain(str, Enum):
    INFORMATION = "Informação"
    LAW = "Lei"
    ECOLOGY = "Ecologia"
    ENERGY = "Energia"
    ECONOMY = "Economia"
    DELIBERATION = "Deliberação"

class Vertex(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    name: str
    domain: ContextDomain
    position: np.ndarray = Field(description="Coordinates in n-dimensional semantic space")
    attributes: Dict[str, Any] = Field(default_factory=dict)
    stability: float = 0.5

class Edge(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    source: str
    target: str
    relation_type: str
    weight: float = 1.0
    transformation: str = "direct"

class Simplex(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    name: str
    vertices: List[str]
    edges: List[tuple] = Field(default_factory=list)
    stability: float = 0.0
    semantic_type: str

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class GeometricManifold(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    dimension: int = 11
    metric: np.ndarray = Field(default_factory=lambda: np.eye(11))

    def model_post_init(self, __context):
        # Ensure metric matches dimension if it was defaulted or passed differently
        if self.metric.shape != (self.dimension, self.dimension):
            self.metric = np.eye(self.dimension)

    def calculate_volume(self) -> float:
        try:
            return float(np.sqrt(np.linalg.det(self.metric)))
        except np.linalg.LinAlgError:
            return float("inf")

    def project_to_shell(self, point: np.ndarray, radius: float = 1.0) -> np.ndarray:
        norm = np.linalg.norm(point)
        if norm < 1e-9:
            rng = np.random.default_rng()
            point = rng.standard_normal(self.dimension)
            norm = np.linalg.norm(point)
        return point * (radius / norm)

    def embed(self, input_data: str) -> np.ndarray:
        seed = int(hash(input_data)) % (2**32)
        rng = np.random.default_rng(seed)
        point = rng.standard_normal(self.dimension)
        return self.project_to_shell(point)

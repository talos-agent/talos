from __future__ import annotations

from typing import List

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class HarmonicMode(BaseModel):
    l: int
    m: int
    amplitude: float
    phase: float
    frequency: float

    def evolve(self, dt: float):
        self.phase = (self.phase + self.frequency * dt) % (2 * np.pi)


class HarmonicCognitionEngine(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    dimension: int = 11
    active_modes: List[HarmonicMode] = Field(default_factory=list)

    def natural_frequency(self, l: int) -> float:
        return float(l * (l + self.dimension - 2))

    def decompose_into_harmonics(self, shell_point: np.ndarray):
        self.active_modes = [
            HarmonicMode(
                l=i,
                m=0,
                amplitude=1.0,
                phase=0.0,
                frequency=self.natural_frequency(i),
            )
            for i in range(5)
        ]

    def evolve_modes(self):
        pass

    def recompose_thought(self) -> np.ndarray:
        return np.random.standard_normal(self.dimension)

    def calculate_integrated_information(self) -> float:
        return 0.95

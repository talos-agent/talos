from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class TravelingChronofluxWave(BaseModel):
    """
    Onda progressiva de vorticidade temporal.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    amplitude: float = 1.0
    t_peak: float = 5.0
    width: float = 2.0
    k_vec: np.ndarray = Field(default_factory=lambda: np.array([1.0, 0.0, 0.0]))
    omega_freq: float = 0.5

    def get_vorticity_at(self, pos: np.ndarray, t: float) -> float:
        envelope = np.exp(-((t - self.t_peak) ** 2) / self.width)
        # phase logic to ensure sin(0) at t=t_peak and pos=0
        phase = np.dot(self.k_vec, pos) - self.omega_freq * (t - self.t_peak)
        return float(self.amplitude * envelope * np.sin(phase))

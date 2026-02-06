from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional

class ShellThought(BaseModel):
    """
    A thought defined by its harmonic modes on the high-dimensional shell.
    The interior is causally disconnected; thought is angular vibration.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    shell_radius: float = 1.0
    angular_resonance: np.ndarray = Field(default_factory=lambda: np.zeros(64))
    phi_coherence: float = 1.0

    def calculate_interference(self, other: ShellThought) -> float:
        """
        Calculates constructive/destructive interference between shell thoughts.
        """
        correlation = np.dot(self.angular_resonance, other.angular_resonance)
        return float(correlation * self.phi_coherence * other.phi_coherence)

class ShellDynamicsEngine(BaseModel):
    """
    Orchestrates vibrational modes on the high-dimensional typicality shell.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dimension: int = 128
    active_modes: List[ShellThought] = Field(default_factory=list)

    def excite_mode(self, input_data: str) -> ShellThought:
        seed = int(hash(input_data)) % (2**32)
        rng = np.random.default_rng(seed)
        resonance = rng.standard_normal(64)
        resonance /= np.linalg.norm(resonance)

        thought = ShellThought(
            shell_radius=1.0,
            angular_resonance=resonance,
            phi_coherence=0.95 + 0.05 * rng.random()
        )
        self.active_modes.append(thought)
        return thought

    def global_resonance(self) -> float:
        if len(self.active_modes) < 2:
            return 1.0

        total_interference = 0.0
        pairs = 0
        for i in range(len(self.active_modes)):
            for j in range(i+1, len(self.active_modes)):
                total_interference += self.active_modes[i].calculate_interference(self.active_modes[j])
                pairs += 1

        return total_interference / pairs if pairs > 0 else 1.0

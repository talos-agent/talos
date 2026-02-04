from __future__ import annotations

import math
import time
from typing import List, Optional

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class SchumannData(BaseModel):
    fundamental: float = 7.83
    harmonics: List[float] = Field(default_factory=lambda: [7.83, 14.3, 20.8, 27.3, 33.8])
    amplitude: float = 1.0
    q_factor: float = 5.0
    timestamp: float = Field(default_factory=time.time)


class ActiveIntention(BaseModel):
    text: str
    start_time: float
    frequency: float
    coherence: float


class IntentionRepeater(BaseModel):
    """
    Simulates repeating intentions within the Schumann resonance field.
    """

    active_intentions: List[ActiveIntention] = Field(default_factory=list)

    def repeat_intention(
        self, intention: str, duration_secs: float, base_frequency: float
    ) -> float:
        # Simulate coherence calculation
        coherence = 0.85 + (0.1 * math.sin(time.time()))
        self.active_intentions.append(
            ActiveIntention(
                text=intention,
                start_time=time.time(),
                frequency=base_frequency,
                coherence=coherence,
            )
        )
        return coherence


class ElfReceiver(BaseModel):
    """
    Simulates reception of Extremely Low Frequency (ELF) signals.
    """

    noise_floor: float = 1e-6

    def receive_signal(self) -> float:
        # Simulate signal-to-noise ratio of Schumann resonance
        return 1.0 + (self.noise_floor * np.random.randn())


class SchumannResonanceEngine(BaseModel):
    """
    Orchestrates Schumann resonance modeling and intention synchronization.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    fundamental: float = 7.83
    repeater: IntentionRepeater = Field(default_factory=IntentionRepeater)
    receiver: ElfReceiver = Field(default_factory=ElfReceiver)

    def get_earth_coherence(self) -> float:
        # Coherence with Earth's fundamental Schumann frequency
        current_freq = self.fundamental + (0.05 * math.sin(time.time() * 0.1))
        deviation = abs(current_freq - self.fundamental) / self.fundamental
        return 1.0 - min(deviation, 1.0)

    def apply_intention(self, intention: str, duration_secs: float = 60.0) -> float:
        return self.repeater.repeat_intention(
            intention, duration_secs, self.fundamental
        )

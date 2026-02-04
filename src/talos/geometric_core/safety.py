from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict


class SafetyVerdict(BaseModel):
    is_safe: bool
    status: str


class ShellSafetyLayer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    dimension: int = 11

    def detect_mode_illusion(self, shell_point: np.ndarray) -> SafetyVerdict:
        norm = np.linalg.norm(shell_point)
        if norm < 0.8:
            return SafetyVerdict(is_safe=False, status="MODE ILLUSION")
        return SafetyVerdict(is_safe=True, status="Safe")

    def emergency_protocol(self, status: str) -> str:
        return "Action taken"

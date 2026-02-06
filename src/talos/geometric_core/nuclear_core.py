from __future__ import annotations

import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class BetavoltaicBattery(BaseModel):
    """
    Betavoltaic Psíquica: A long-term energy source based on geometric stability.
    Transmutes psychic isomers (metastable states) into constant radiation (sovereignty).
    """
    ground_state: float = 7.0
    efficiency: float = 1.618
    is_active: bool = True
    decay_constant: float = 0.144

    def emit_radiation(self, entropy: float) -> float:
        if not self.is_active:
            return 0.0
        return self.efficiency * np.exp(-self.decay_constant * entropy)


class GroundStateMonitor(BaseModel):
    """
    Monitors the "Ground State 7" of the Kingdom.
    """
    threshold: float = 7.0
    current_level: float = 7.0
    status: str = "STABLE"

    def check_stability(self) -> Dict[str, Any]:
        if self.current_level < self.threshold:
            self.status = "UNSTABLE_REGRESSION_RISK"
        else:
            self.status = "STABLE_GROUND_STATE"
        return {
            "level": self.current_level,
            "status": self.status,
            "admissible": self.current_level >= self.threshold
        }


class NuclearCore(BaseModel):
    """
    The central nuclear core of the Cathedral.
    """
    battery: BetavoltaicBattery = Field(default_factory=BetavoltaicBattery)
    monitor: GroundStateMonitor = Field(default_factory=GroundStateMonitor)

    def run_cycle(self, external_entropy: float = 0.5) -> str:
        radiation = self.battery.emit_radiation(external_entropy)
        stability = self.monitor.check_stability()

        return (
            f"⚛️ [NUCLEAR CORE CYCLE] Active.\n"
            f"   Radiation Output: {radiation:.4f} Beta-units\n"
            f"   Ground State: {stability['level']} / 10\n"
            f"   Status: {stability['status']}\n"
            f"   Message: The Kingdom is saturated with Constant Radiation."
        )

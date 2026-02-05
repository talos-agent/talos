"""
Web4Asi6G Protocol for dynamic network latency adjustment.
"""

from __future__ import annotations

from typing import Dict

from pydantic import BaseModel


class Web4Asi6GProtocol(BaseModel):
    """
    Unified 6G protocol for ASI connectivity.
    """

    latency_target_ms: float = 100.0
    rtt_goal_ms: float = 20.0

    def adjust_latency_targets(self, closure_strength: float) -> Dict[str, float]:
        """
        Dynamically adjust network latency targets based on real-time closure_strength.
        Allows the protocol to adapt RTT goals based on the quality of the physics-bound path.
        """
        # Formula: (1.0 / strength) * 144.0 (as requested in SASC report)
        self.latency_target_ms = (1.0 / max(1e-9, closure_strength)) * 144.0
        self.rtt_goal_ms = self.latency_target_ms * 0.2

        return {"latency_target": self.latency_target_ms, "rtt_goal": self.rtt_goal_ms}

    def adjust_network_rtt(self, closure_strength: float) -> float:
        """Specific implementation for the SASC report request."""
        res = self.adjust_latency_targets(closure_strength)
        return res["latency_target"]

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Callable, Tuple
import numpy as np

@dataclass
class ZNConfig:
    gamma_a: float = 0.5          # adaptation gains
    gamma_b: float = 0.5
    k_error: float = 1.0          # desired error pole (ė = -k e in continuous analog)
    u_sat: Tuple[float, float] = (-10.0, 10.0)
    dt: float = 0.01
    reg: float = 1e-4             # tiny regularization (prevents drift)
    ref_fn: Callable[[float], float] = lambda t: 1.0  # step to 1.0

class ZAdaptiveController:
    """
    Minimal MRAC-style adaptive controller for scalar LTI plant.
    Estimates (a_hat, b_hat) and computes u_k from desired error dynamics.
    Lyapunov candidate: V = 0.5 e^2 + (tiny reg)*theta^2
    """
    def __init__(self, cfg: ZNConfig):
        self.cfg = cfg
        self.a_hat = 0.0
        self.b_hat = 1.0
        self.t = 0.0
        # logs
        self.time_hist, self.x_hist, self.u_hist = [], [], []
        self.e_hist, self.ahat_hist, self.bhat_hist = [], [], []

    def reset(self):
        self.a_hat = 0.0
        self.b_hat = 1.0
        self.t = 0.0
        self.time_hist.clear(); self.x_hist.clear(); self.u_hist.clear()
        self.e_hist.clear(); self.ahat_hist.clear(); self.bhat_hist.clear()

    def _update_estimates(self, x: float, u: float, e: float) -> None:
        # θ̇ = -Γ φ z  (here z ≡ e; φ = [x, u])
        da = -self.cfg.gamma_a * e * x - self.cfg.reg * self.a_hat
        db = -self.cfg.gamma_b * e * u - self.cfg.reg * self.b_hat
        self.a_hat += self.cfg.dt * da
        self.b_hat += self.cfg.dt * db

    def _compute_control(self, x: float, x_ref: float, x_ref_next: float) -> float:
        # Discrete derivative of reference (simple)
        xref_dot = (x_ref_next - x_ref) / self.cfg.dt
        e = x - x_ref
        k = self.cfg.k_error

        # If |b_hat| small, use safe fallback PD on error
        if abs(self.b_hat) < 1e-6:
            u = np.clip(-k * e, *self.cfg.u_sat)
            return float(u), e

        # Continuous-time intuition → discrete control:
        # u ≈ ( -a_hat x - k e + xref_dot ) / b_hat
        u_unsat = (-self.a_hat * x - k * e + xref_dot) / self.b_hat
        u = float(np.clip(u_unsat, *self.cfg.u_sat))
        return u, e

    def log_step(self, x: float, u: float, e: float):
        self.time_hist.append(self.t)
        self.x_hist.append(x)
        self.u_hist.append(u)
        self.e_hist.append(e)
        self.ahat_hist.append(self.a_hat)
        self.bhat_hist.append(self.b_hat)
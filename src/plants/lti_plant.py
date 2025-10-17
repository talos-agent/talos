from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class LTIPlant:
    """Discrete-time scalar plant: x_{k+1} = (1+dt*a) x_k + dt*b u_k + w_k"""
    a: float = -0.4         # true but unknown to controller
    b: float = 0.8          # true but unknown to controller
    dt: float = 0.01
    w_std: float = 0.0      # process noise std

    x: float = 0.0          # state

    def reset(self, x0: float = 0.0) -> None:
        self.x = float(x0)

    def step(self, u: float) -> float:
        A = 1.0 + self.dt * self.a
        B = self.dt * self.b
        w = np.random.normal(0.0, self.w_std) if self.w_std > 0 else 0.0
        self.x = A * self.x + B * float(u) + w
        return self.x
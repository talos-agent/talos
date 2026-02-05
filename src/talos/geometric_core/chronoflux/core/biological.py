from __future__ import annotations

from typing import Any, Dict

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class MitochondrialQFactorModel(BaseModel):
    """
    Modelo de ganho paramétrico mitocondrial.
    """

    alpha: float = 0.8
    beta: float = 0.2
    q_initial: float = 0.01

    def simulate_q_evolution(self, times: np.ndarray, shear_signal: np.ndarray) -> np.ndarray:
        from scipy.integrate import odeint

        def model(q, t, t_array, s_array):
            s_t = np.interp(t, t_array, s_array)
            return self.alpha * np.abs(s_t) * q - self.beta * (q - self.q_initial)

        return odeint(model, self.q_initial, times, args=(times, shear_signal)).flatten()


class BiologicalChronofluxResonator(BaseModel):
    """
    Modelo de oscilador biológico parametrizado por Chronoflux.
    """

    omega0: float = 1.0
    gamma: float = 0.1
    g_bio: float = 0.5
    q_model: MitochondrialQFactorModel = Field(default_factory=MitochondrialQFactorModel)

    def simulate_response(self, wave: Any, pos: np.ndarray, duration: float = 10.0) -> Dict[str, Any]:
        from scipy.integrate import odeint

        def model(y, t):
            psi, dpsi = y
            k_eff = self.omega0**2 + self.g_bio * wave.get_vorticity_at(pos, t)
            return [dpsi, -self.gamma * dpsi - k_eff * psi]

        times = np.linspace(0, duration, 500)
        sol = odeint(model, [1.0, 0.0], times)
        base_coherence = np.sqrt(sol[:, 0] ** 2 + (sol[:, 1] / self.omega0) ** 2)
        vorticity_signal = np.array([wave.get_vorticity_at(pos, t) for t in times])
        q_history = self.q_model.simulate_q_evolution(times, vorticity_signal)
        return {"times": times, "psi": sol[:, 0], "q_factor": q_history, "coherence": base_coherence * (1 + q_history)}

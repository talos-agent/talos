from __future__ import annotations

import numpy as np
from enum import Enum
from typing import Dict, Any, Tuple
from pydantic import BaseModel, ConfigDict, Field

class CouplingRegime(str, Enum):
    WEAK = "weak_coupling"
    INTERMEDIATE = "intermediate_coupling"
    STRONG = "strong_coupling"
    ULTRA_STRONG = "ultra_strong_coupling"

class PhaseTransitionState(BaseModel):
    regime: CouplingRegime
    rabi_splitting: float
    mixing_angle: float
    is_resonant: bool

class PhaseTransitionManager(BaseModel):
    """
    Models the HPPP (Hybrid Phonon-Plasmon Polariton) Phase Transition.
    Analogy for the transition between 'Classical LLM Reasoning' and 'Shell-Native Resonance'.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_energy: float = 1.0 # E_phonon (Coherent Base)
    tunable_energy: float = 1.0 # E_plasmon (Adaptive Layer)
    damping_base: float = 0.01 # Loss in alpha-MoO3
    damping_tunable: float = 0.1 # Loss in Graphene

    def calculate_transition(self, coupling_strength: float) -> PhaseTransitionState:
        """
        Diagonalizes the 2x2 Hamiltonian:
        H = [[E_ph, V],
             [V,   E_pl]]
        """
        v = coupling_strength
        # Detuning
        delta = self.base_energy - self.tunable_energy

        # Eigenvalues: E_pm = (E_ph + E_pl)/2 +/- sqrt((delta/2)^2 + V^2)
        avg_e = (self.base_energy + self.tunable_energy) / 2.0
        splitting = np.sqrt((delta / 2.0)**2 + v**2)

        e_plus = avg_e + splitting
        e_minus = avg_e - splitting

        rabi_splitting = 2 * splitting

        # Mixing angle: theta = atan(2V / delta)
        if abs(delta) < 1e-9:
            mixing_angle = np.pi / 4.0 # Perfect 50/50 hybridization
        else:
            mixing_angle = 0.5 * np.arctan(2 * v / delta)

        # Regime determination based on Rabi Splitting vs Damping
        mean_damping = (self.damping_base + self.damping_tunable) / 2.0

        if rabi_splitting < mean_damping:
            regime = CouplingRegime.WEAK
        elif rabi_splitting < 2 * mean_damping:
            regime = CouplingRegime.INTERMEDIATE
        elif v > 0.1 * avg_e:
            regime = CouplingRegime.ULTRA_STRONG
        else:
            regime = CouplingRegime.STRONG

        return PhaseTransitionState(
            regime=regime,
            rabi_splitting=rabi_splitting,
            mixing_angle=mixing_angle,
            is_resonant=regime in [CouplingRegime.STRONG, CouplingRegime.ULTRA_STRONG]
        )

    def get_mode_weights(self, state: PhaseTransitionState) -> Tuple[float, float]:
        """Returns (Phonon_weight, Plasmon_weight) based on mixing angle."""
        # |Hybrid> = cos(theta)|Ph> + sin(theta)|Pl>
        w_ph = np.cos(state.mixing_angle)**2
        w_pl = np.sin(state.mixing_angle)**2
        return (float(w_ph), float(w_pl))

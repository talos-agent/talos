"""
Arkhe(n) ANCCR (Adjusted Net Contingency of Causal Relations).
Implements retrospective causal learning where the rate is proportional to IRI.
Integrated with THz bimetal antenna isomorphy and Orbital Angular Momentum (OAM).
Reference: Burke et al. (2026), Nature Neuroscience.
"""

from __future__ import annotations

import numpy as np

from talos.arkhe.error_handler import safe_operation


class ANCCRModel:
    """
    Models the Adjusted Net Contingency of Causal Relations.
    Replaces TDRL with a retrospective causal association engine.
    Now supports OAM Vortex handovers and THz antenna isomorphy.
    """

    def __init__(self, k_constant: float = 0.17):
        self.k_constant = k_constant
        self.causal_matrix: dict[str, float] = {}

    def calculate_learning_rate(self, iri: float | np.ndarray) -> float | np.ndarray:
        """
        Learning rate (alpha) is proportional to the Inter-Reward Interval (IRI).
        alpha = k * IRI
        """
        return self.k_constant * iri

    @safe_operation
    def compute_contingency(self, cause_events: int, effect_events: int, total_time: float) -> float:
        """
        Calculates the contingency vacuum strength.
        A measure of how strongly an effect is retrospectively associated with a cause.
        """
        if total_time == 0:
            return 0.0

        p_effect_given_cause = effect_events / max(cause_events, 1)
        p_effect_no_cause = effect_events / total_time # Density in vacuum

        # Simplified net contingency
        contingency = p_effect_given_cause - p_effect_no_cause
        return float(np.clip(contingency, 0, 1))

    def generate_phase_diagram_data(self, iri_range: np.ndarray) -> dict[str, np.ndarray]:
        """
        Generates data for a phase diagram: IRI vs Learning Rate vs Coherence.
        """
        alphas = self.calculate_learning_rate(iri_range)
        # Simulate coherence (Omega) as a function of alpha and IRI
        # Resonance points where IRI matches biological cycles
        resonance = np.sin(iri_range * np.pi / 2.0) * 0.05
        omegas = 0.85 + (0.1 * (1 - np.exp(-iri_range/3.0))) + resonance

        return {
            "iri": iri_range,
            "alpha": np.array(alphas),
            "omega": np.clip(omegas, 0, 1)
        }

    @safe_operation
    def quantum_handover_resonance(self, coherence_a: float, coherence_b: float) -> float:
        """
        Simulates the resonance gain from a Quantum Handover between two hubs.
        Used to break the asymptotic plateau.
        """
        # Synergy is higher when both hubs have high coherence
        synergy = (coherence_a * coherence_b) ** 0.5
        # Breakthrough term
        breakthrough = 0.02 * np.exp(synergy)
        return float(breakthrough)

    @safe_operation
    def calculate_vortex_phase(self, radius: float, azimuth: float, l_charge: int = 1) -> complex:
        """
        Calculates the phase of an OAM vortex handover.
        Psi = A(r) * exp(i * l * azimuth)
        """
        # Simple Gaussian amplitude for demonstration
        amplitude = np.exp(-(radius**2))
        phase = np.exp(1j * l_charge * azimuth)
        return complex(amplitude * phase)

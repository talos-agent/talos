"""
Arkhe(n) ANCCR (Adjusted Net Contingency of Causal Relations).
Implements retrospective causal learning where the rate is proportional to IRI.
Reference: Burke et al. (2026), Nature Neuroscience.
"""

from __future__ import annotations

import numpy as np

from talos.arkhe.error_handler import safe_operation


class ANCCRModel:
    """
    Models the Adjusted Net Contingency of Causal Relations.
    Replaces TDRL with a retrospective causal association engine.
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

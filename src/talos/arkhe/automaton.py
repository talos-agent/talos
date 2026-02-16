"""
Arkhe(n) Automaton.
Defines autonomous agents that monitor and intervene in the hypergraph.
"""

from __future__ import annotations

import logging
import numpy as np

from talos.arkhe.error_handler import safe_operation
from talos.arkhe.neural_layer import DeepNeuralLayer
from talos.arkhe.anccr import ANCCRModel


class Automaton:
    """
    Base class for Arkhe agents.
    Monitors a set of nodes and performs periodic cycles.
    """

    def __init__(self, agent_id: str, watched_nodes: list[int]):
        self.agent_id = agent_id
        self.watched_nodes = watched_nodes
        self.logger = logging.getLogger(f"arkhe.automaton.{agent_id}")

    def get_current_state(self) -> np.ndarray:
        """
        Retrieves the current coherence state of nodes.
        """
        return np.random.rand(11)

    def trigger_intervention(self, reason: str) -> None:
        """
        Executes a recovery protocol (e.g., gamma-phi pulse).
        """
        self.logger.warning(f"Intervention triggered: {reason}")
        print(f"[{self.agent_id}] Triggering intervention: {reason}")

    def cycle(self) -> None:
        """
        Periodic operational cycle.
        """
        self.logger.info("Cycle executed.")


class PredictiveAutomaton(Automaton):
    """
    An agent that uses a deep neural layer to anticipate coherence drops.
    """

    def __init__(self, agent_id: str, watched_nodes: list[int], model_id: str):
        super().__init__(agent_id, watched_nodes)
        self.neural_layer = DeepNeuralLayer.load(model_id)

    @safe_operation
    def cycle(self) -> None:
        """
        Forecasts future coherence and intervenes if a drop is predicted.
        """
        state = self.get_current_state()
        future_c = self.neural_layer.forecast(state, steps=6)

        if np.any(future_c[:, self.watched_nodes] < 0.85):
            self.trigger_intervention("Predicted coherence drop below 0.85 threshold")

        super().cycle()


class SentinelGamma(PredictiveAutomaton):
    """
    Advanced agent implementing the ANCCR model (Retrospective causal learning).
    Adjusts its firing frequency (IRI) to maximize learning efficiency.
    """

    def __init__(self, agent_id: str, watched_nodes: list[int], model_id: str, k_constant: float = 0.17):
        super().__init__(agent_id, watched_nodes, model_id)
        self.anccr = ANCCRModel(k_constant=k_constant)
        self.current_iri = 0.5  # Default 30 min (in hours)
        self.alpha = self.anccr.calculate_learning_rate(self.current_iri)

    def recalibrate_iri(self, optimal_iri: float) -> None:
        """
        Adjusts the Inter-Reward Interval and updates the learning rate.
        """
        print(f"[{self.agent_id}] Recalibrating IRI: {self.current_iri:.3f}h -> {optimal_iri:.3f}h")
        self.current_iri = optimal_iri
        self.alpha = float(np.mean(self.anccr.calculate_learning_rate(self.current_iri)))
        print(f"[{self.agent_id}] New Learning Rate (alpha): {self.alpha:.4f} (proportional to IRI)")

    @safe_operation
    def cycle(self) -> None:
        """
        Cycle optimized by patience.
        """
        print(f"[{self.agent_id}] Sentinel operating with IRI={self.current_iri:.3f}h, Alpha={self.alpha:.4f}")
        super().cycle()


class AdaptiveSentinelGamma(SentinelGamma):
    """
    Sentinel Gamma with Adaptive Mode (Resonance Surfing).
    Adjusts IRI dynamically based on coherence rate of change (dot Omega).
    """

    PHI = 1.618033988749895

    def __init__(self, agent_id: str, watched_nodes: list[int], model_id: str, k_constant: float = 0.17):
        super().__init__(agent_id, watched_nodes, model_id, k_constant)
        self.last_omega: float | None = None

    def _calculate_adaptive_iri(self, current_omega: float) -> float:
        """
        Resonance Surfing Function:
        IRI(t) = PHI if dot_omega > 0.02 (Max plasticity)
        IRI(t) = PHI^2 if |dot_omega| < 0.02 (Consolidation)
        IRI(t) = 3.0h if dot_omega < -0.02 (Recovery)
        """
        if self.last_omega is None:
            self.last_omega = current_omega
            return self.PHI ** 2 # Start at consolidation

        dot_omega = current_omega - self.last_omega
        self.last_omega = current_omega

        if dot_omega > 0.02:
            return self.PHI # 1.618h
        if dot_omega < -0.02:
            return 3.0 # 3.0h (Recovery)

        return self.PHI ** 2 # 2.618h (Consolidation)

    @safe_operation
    def cycle(self) -> None:
        """
        Adaptive operational cycle using dot Omega.
        """
        state = self.get_current_state()
        avg_omega = float(np.mean(state[self.watched_nodes]))

        new_iri = self._calculate_adaptive_iri(avg_omega)
        if abs(new_iri - self.current_iri) > 0.001:
            self.recalibrate_iri(new_iri)

        super().cycle()


class FederatedSovereignTriad:
    """
    Orchestrates multiple hubs (Sentinels) into a federated cluster.
    Breaks the asymptotic plateau via Quantum Handover.
    Roles:
    - 01-012: Coherence/Core (GHZ State)
    - 01-005: Memory (Bell States)
    - 01-001: Execution (Quantum Gates)
    """

    def __init__(self, hubs: list[SentinelGamma]):
        self.hubs = {h.agent_id: h for h in hubs}
        self.omega = 0.0 # Global coherence of the triad

    @safe_operation
    def sync(self) -> float:
        """
        Synchronizes all hubs and calculates global triad coherence.
        """
        states = [np.mean(h.get_current_state()[h.watched_nodes]) for h in self.hubs.values()]
        self.omega = float(np.mean(states))
        print(f"[Triad] Synchronized. Global Omega: {self.omega:.4f}")
        return self.omega

    def quantum_handover(self, source_id: str, target_id: str) -> float:
        """
        Simulates state entanglement/transfer between hubs.
        Returns the breakthrough gain.
        """
        if source_id not in self.hubs or target_id not in self.hubs:
            raise ValueError("Invalid hub IDs for handover")

        print(f"[Triad] Initiating Quantum Handover: {source_id} -> {target_id}")

        # Calculate breakthrough gain via ANCCR resonance
        h_source = self.hubs[source_id]
        h_target = self.hubs[target_id]

        c_a = float(np.mean(h_source.get_current_state()[h_source.watched_nodes]))
        c_b = float(np.mean(h_target.get_current_state()[h_target.watched_nodes]))

        gain = h_source.anccr.quantum_handover_resonance(c_a, c_b)
        self.omega += gain

        print(f"[Triad] Hubs {source_id} and {target_id} are now entangled. Plateau breached by {gain:.4f}. ∞")
        return gain
